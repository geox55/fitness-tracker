"""Бизнес-операции auth-домена. Не зависит от FastAPI."""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_settings
from ...security import (
    TokenInvalidError,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from .models import AuthToken, User

# TTL для одноразовых токенов (REQ-03, REQ-04).
EMAIL_VERIFY_TTL = timedelta(hours=24)
PASSWORD_RESET_TTL = timedelta(hours=1)

OneTimeTokenType = Literal["email_verify", "password_reset"]


class AuthError(Exception):
    code: str = "auth_error"


class EmailTakenError(AuthError):
    code = "email_taken"


class InvalidCredentialsError(AuthError):
    code = "invalid_credentials"


class UserNotFoundError(AuthError):
    code = "not_found"


class RefreshTokenInvalidError(AuthError):
    """Refresh-токен подписан валидно, но запись отсутствует/просрочена/пустая."""

    code = "refresh_invalid"


class RefreshTokenReusedError(AuthError):
    """Refresh-токен с used_at IS NOT NULL — индикатор кражи. Нужна реакция."""

    code = "refresh_reused"


class EmailNotConfirmedError(AuthError):
    """Логин на аккаунт со status=unconfirmed (REQ-03 + Scenario 2.3)."""

    code = "email_unconfirmed"


class OneTimeTokenInvalidError(AuthError):
    """Токен (email_verify / password_reset) не найден, истёк или уже использован."""

    code = "token_invalid"


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def register_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    name: str | None = None,
) -> User:
    """Создать аккаунт. email_status зависит от feature-flag:
    - email_verification_required=True  → 'unconfirmed', нужен verify-flow.
    - email_verification_required=False → сразу 'active', можно логиниться.

    Если передано `name` — сразу создаём UserProfile с этим именем,
    чтобы пользователь не видел пустое поле в профиле и не вводил
    то же самое второй раз (UX REQ).
    """
    settings = get_settings()
    initial_status = (
        "unconfirmed" if settings.email_verification_required else "active"
    )
    user = User(
        email=email.lower(),
        password_hash=hash_password(password),
        email_status=initial_status,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise EmailTakenError() from exc

    if name is not None:
        # Лениво импортируем профиль, чтобы не тянуть его модель в auth-сервис
        # на старте (auth.service используется и в /auth/login без профиля).
        from ..profile.models import UserProfile

        profile = UserProfile(user_id=user.id, name=name.strip() or None)
        session.add(profile)
        await session.flush()
    return user


async def authenticate(
    session: AsyncSession, *, email: str, password: str
) -> User:
    """Найти и проверить аккаунт. Не проверяет email_status — это делает caller
    после получения user, чтобы можно было различать причины отказа в логике
    логина (401 vs 403)."""
    stmt = select(User).where(
        User.email == email.lower(), User.deleted_at.is_(None)
    )
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    return user


async def authenticate_for_login(
    session: AsyncSession, *, email: str, password: str
) -> User:
    """То же самое + проверка status=active (REQ-03), если включена верификация."""
    user = await authenticate(session, email=email, password=password)
    if get_settings().email_verification_required and user.email_status != "active":
        raise EmailNotConfirmedError()
    return user


async def issue_token_pair(
    session: AsyncSession, *, user_id: uuid.UUID
) -> tuple[str, str, int]:
    """Выдать access + refresh; refresh-tokenы хранятся хэшем в БД."""
    settings = get_settings()
    access, _ = create_token(user_id=user_id, kind="access")
    refresh, refresh_exp = create_token(user_id=user_id, kind="refresh")
    session.add(
        AuthToken(
            user_id=user_id,
            type="refresh",
            token_hash=_hash_token(refresh),
            expires_at=refresh_exp,
        )
    )
    return access, refresh, settings.access_token_ttl_seconds


async def get_user_by_id(
    session: AsyncSession, user_id: uuid.UUID
) -> User:
    user = await session.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise UserNotFoundError()
    return user


async def user_id_from_access_token(token: str) -> uuid.UUID:
    payload = decode_token(token, expected_kind="access")
    sub = payload.get("sub")
    if sub is None:
        raise TokenInvalidError("Token missing sub")
    return uuid.UUID(sub)


def is_token_expired(t: AuthToken) -> bool:
    expires_at = t.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at <= datetime.now(UTC)


async def _invalidate_all_refresh_tokens(
    session: AsyncSession, *, user_id: uuid.UUID
) -> None:
    """Помечаем used_at = now() для всех активных refresh-токенов пользователя.

    Используется при подозрении на кражу (повторное использование уже-обменянного
    refresh-токена) — выбиваем все сессии разом.
    """
    await session.execute(
        update(AuthToken)
        .where(
            AuthToken.user_id == user_id,
            AuthToken.type == "refresh",
            AuthToken.used_at.is_(None),
        )
        .values(used_at=datetime.now(UTC))
    )


RefreshOutcome = Literal["valid", "not_found", "reused", "expired"]


def classify_refresh_record(record: AuthToken | None) -> RefreshOutcome:
    """Чистая логика-классификатор: что делать с найденной (или нет) строкой.

    Вынесена отдельно, чтобы тестировать без БД: правила достаточно тонкие
    (порядок проверок reused-vs-expired важен для безопасности — reused
    приоритетнее, иначе атакующий с просроченным украденным токеном получит
    более мягкий ответ).
    """
    if record is None:
        return "not_found"
    if record.used_at is not None:
        return "reused"
    if is_token_expired(record):
        return "expired"
    return "valid"


async def rotate_refresh_token(
    session: AsyncSession, *, refresh_token: str
) -> tuple[str, str, int]:
    """Обменять refresh на новую пару (rotation + reuse-detection).

    Если строка помечена как used — это либо race, либо кража: выбиваем все
    активные refresh-токены пользователя и поднимаем RefreshTokenReusedError.
    """
    payload = decode_token(refresh_token, expected_kind="refresh")
    sub = payload.get("sub")
    if sub is None:
        raise TokenInvalidError("Token missing sub")
    user_id = uuid.UUID(sub)

    token_hash = _hash_token(refresh_token)
    stmt = select(AuthToken).where(
        AuthToken.token_hash == token_hash,
        AuthToken.type == "refresh",
    )
    record = (await session.execute(stmt)).scalar_one_or_none()

    outcome = classify_refresh_record(record)
    if outcome == "not_found":
        raise RefreshTokenInvalidError("refresh token not found")
    if outcome == "reused":
        assert record is not None  # для mypy: reused ⇒ record существует
        await _invalidate_all_refresh_tokens(session, user_id=record.user_id)
        # Коммитим ДО raise: иначе get_session ловит exception, делает rollback
        # и инвалидация теряется. Это security-критично, поэтому ломаем общее
        # правило "сервис не коммитит" — здесь side-effect должен быть стойким.
        await session.commit()
        raise RefreshTokenReusedError(
            "refresh token already used; all sessions invalidated"
        )
    if outcome == "expired":
        raise RefreshTokenInvalidError("refresh token expired")

    assert record is not None  # outcome == "valid" ⇒ record существует
    record.used_at = datetime.now(UTC)
    return await issue_token_pair(session, user_id=user_id)


async def revoke_refresh_token(
    session: AsyncSession, *, refresh_token: str
) -> None:
    """Logout: пометить конкретный refresh-токен как использованный.

    Идемпотентно: если токен уже used или не существует — успех без ошибки,
    логаут не должен ронять клиент.
    """
    try:
        decode_token(refresh_token, expected_kind="refresh")
    except TokenInvalidError:
        return  # уже невалиден — логаут идемпотентен
    token_hash = _hash_token(refresh_token)
    await session.execute(
        update(AuthToken)
        .where(
            AuthToken.token_hash == token_hash,
            AuthToken.type == "refresh",
            AuthToken.used_at.is_(None),
        )
        .values(used_at=datetime.now(UTC))
    )


# ---- Одноразовые токены: email_verify / password_reset ----------------------


def _generate_one_time_token() -> str:
    """URL-safe random token. 32 байта = 256 бит, достаточно для anti-bruteforce."""
    return secrets.token_urlsafe(32)


async def issue_one_time_token(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    kind: OneTimeTokenType,
) -> str:
    """Сгенерировать и сохранить одноразовый токен. Возвращает raw-значение
    (его кладём в письмо); в БД хранится только хэш (NFR-01)."""
    ttl = EMAIL_VERIFY_TTL if kind == "email_verify" else PASSWORD_RESET_TTL
    raw = _generate_one_time_token()
    session.add(
        AuthToken(
            user_id=user_id,
            type=kind,
            token_hash=_hash_token(raw),
            expires_at=datetime.now(UTC) + ttl,
        )
    )
    return raw


async def _consume_one_time_token(
    session: AsyncSession,
    *,
    raw_token: str,
    kind: OneTimeTokenType,
) -> AuthToken:
    """Найти, провалидировать и пометить как использованный. Атомарно через
    flush(): если две попытки подойдут параллельно, вторая увидит used_at."""
    token_hash = _hash_token(raw_token)
    stmt = select(AuthToken).where(
        AuthToken.token_hash == token_hash, AuthToken.type == kind
    )
    record = (await session.execute(stmt)).scalar_one_or_none()
    if record is None or record.used_at is not None or is_token_expired(record):
        raise OneTimeTokenInvalidError()
    record.used_at = datetime.now(UTC)
    return record


async def verify_email(session: AsyncSession, *, raw_token: str) -> User:
    """Спека 001 Scenario 2: подтверждение email. Возвращает активированного user."""
    record = await _consume_one_time_token(
        session, raw_token=raw_token, kind="email_verify"
    )
    user = await session.get(User, record.user_id)
    if user is None:
        raise OneTimeTokenInvalidError()
    if user.email_status != "active":
        user.email_status = "active"
    return user


async def request_password_reset(
    session: AsyncSession, *, email: str
) -> tuple[User, str] | None:
    """Если пользователь существует — вернуть (user, raw_token), иначе None.

    Caller отправляет письмо только если результат не None, но клиенту в любом
    случае отвечает 'письмо отправлено' (NFR-04: timing-safe против утечки
    наличия аккаунта).
    """
    stmt = select(User).where(
        User.email == email.lower(), User.deleted_at.is_(None)
    )
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        return None
    raw = await issue_one_time_token(session, user_id=user.id, kind="password_reset")
    return user, raw


async def reset_password(
    session: AsyncSession, *, raw_token: str, new_password: str
) -> User:
    """Спека 001 Scenario 4 + REQ-09: при смене пароля все активные refresh
    выбиваются."""
    record = await _consume_one_time_token(
        session, raw_token=raw_token, kind="password_reset"
    )
    user = await session.get(User, record.user_id)
    if user is None or user.deleted_at is not None:
        raise OneTimeTokenInvalidError()
    user.password_hash = hash_password(new_password)
    await _invalidate_all_refresh_tokens(session, user_id=user.id)
    return user


async def delete_account(
    session: AsyncSession, *, user: User, password_confirmation: str
) -> None:
    """Soft-delete + инвалидация всех сессий. Hard-delete с физической очисткой
    PII делается отдельным фоновым джобом за ≤30 дней (REQ-11)."""
    if not verify_password(password_confirmation, user.password_hash):
        raise InvalidCredentialsError()
    user.deleted_at = datetime.now(UTC)
    await _invalidate_all_refresh_tokens(session, user_id=user.id)
