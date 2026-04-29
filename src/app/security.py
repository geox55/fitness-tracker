"""Хэширование паролей и подпись JWT.

Спецификации: 001-auth.md и docs/architecture/07-security.md.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from .config import get_settings

# Параметры argon2id вне топ-функций — чтобы PasswordHasher переиспользовался.
_hasher = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=4)


def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    return True


JwtKind = Literal["access", "refresh"]


def create_token(
    *,
    user_id: uuid.UUID,
    kind: JwtKind,
    jti: uuid.UUID | None = None,
) -> tuple[str, datetime]:
    """Возвращает (token, expires_at)."""
    settings = get_settings()
    now = datetime.now(UTC)
    ttl = (
        settings.access_token_ttl_seconds
        if kind == "access"
        else settings.refresh_token_ttl_seconds
    )
    expires_at = now + timedelta(seconds=ttl)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": kind,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(jti or uuid.uuid4()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_at


class TokenInvalidError(Exception):
    pass


def decode_token(token: str, *, expected_kind: JwtKind) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenInvalidError("Token is invalid or expired") from exc
    if payload.get("type") != expected_kind:
        raise TokenInvalidError(f"Expected token of type '{expected_kind}'")
    return payload
