"""Auth endpoints — spec 001."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from ...config import get_settings
from ...domains.auth.models import User
from ...domains.auth.rate_limit import get_login_tracker
from ...domains.auth.schemas import (
    DeleteAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenPair,
    VerifyEmailRequest,
)
from ...domains.auth.service import (
    EmailNotConfirmedError,
    EmailTakenError,
    InvalidCredentialsError,
    OneTimeTokenInvalidError,
    RefreshTokenInvalidError,
    RefreshTokenReusedError,
    authenticate_for_login,
    delete_account,
    issue_one_time_token,
    issue_token_pair,
    register_user,
    request_password_reset,
    reset_password,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_email,
)
from ...email import get_email_sender
from ...security import TokenInvalidError
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: RegisterRequest, session: SessionDep) -> RegisterResponse:
    try:
        user = await register_user(
            session, email=payload.email, password=payload.password
        )
    except EmailTakenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "email_taken",
                "message": "Аккаунт с этим email уже существует.",
            },
        ) from exc
    if get_settings().email_verification_required:
        raw = await issue_one_time_token(
            session, user_id=user.id, kind="email_verify"
        )
        await get_email_sender().send_email_verification(
            to=user.email, token=raw
        )
    return RegisterResponse(user_id=user.id, email_status=user.email_status)


@router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest, session: SessionDep, response: Response
) -> TokenPair:
    tracker = get_login_tracker()
    key = payload.email.lower()
    now = datetime.now(UTC)

    retry_after = tracker.is_locked(key, now)
    if retry_after is not None:
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limited",
                "message": "Слишком много попыток. Попробуйте через 15 минут.",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    try:
        user = await authenticate_for_login(
            session, email=payload.email, password=payload.password
        )
    except InvalidCredentialsError as exc:
        # Неудача — двигаем счётчик. EmailNotConfirmedError тоже считается
        # успешной аутентификацией с т.з. brute-force (пароль был верный),
        # поэтому её НЕ записываем как failure.
        tracker.record_failure(key, now)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_credentials",
                "message": "Неверный email или пароль.",
            },
        ) from exc
    except EmailNotConfirmedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "email_unconfirmed",
                "message": (
                    "Подтвердите email — мы отправили письмо при регистрации."
                ),
            },
        ) from exc

    tracker.record_success(key, now)
    access, refresh, ttl = await issue_token_pair(session, user_id=user.id)
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=ttl)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, session: SessionDep) -> TokenPair:
    try:
        access, new_refresh, ttl = await rotate_refresh_token(
            session, refresh_token=payload.refresh_token
        )
    except RefreshTokenReusedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "refresh_reused",
                "message": (
                    "Этот refresh-токен уже использовался. "
                    "Все сессии завершены, войдите заново."
                ),
            },
        ) from exc
    except (RefreshTokenInvalidError, TokenInvalidError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "refresh_invalid",
                "message": "Refresh-токен недействителен.",
            },
        ) from exc
    return TokenPair(
        access_token=access, refresh_token=new_refresh, expires_in=ttl
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, session: SessionDep) -> None:
    await revoke_refresh_token(session, refresh_token=payload.refresh_token)


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify(payload: VerifyEmailRequest, session: SessionDep) -> None:
    try:
        await verify_email(session, raw_token=payload.token)
    except OneTimeTokenInvalidError as exc:
        # Spec 001 Edge Case: уже-использованный токен → 410.
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "error": "token_invalid",
                "message": "Ссылка недействительна или уже использована.",
            },
        ) from exc


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
async def resend_verification(
    payload: ResendVerificationRequest, session: SessionDep
) -> dict[str, str]:
    """Повторно выпускает email_verify токен. Отвечаем одинаково и для
    несуществующего email (NFR-04)."""
    stmt = select(User).where(User.email == payload.email.lower())
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is not None and user.email_status != "active":
        raw = await issue_one_time_token(
            session, user_id=user.id, kind="email_verify"
        )
        await get_email_sender().send_email_verification(to=user.email, token=raw)
    return {"status": "sent_if_eligible"}


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    payload: ForgotPasswordRequest, session: SessionDep
) -> dict[str, str]:
    """NFR-04: одинаковый ответ независимо от наличия email в базе."""
    result = await request_password_reset(session, email=payload.email)
    if result is not None:
        user, raw = result
        await get_email_sender().send_password_reset(to=user.email, token=raw)
    return {"status": "sent_if_eligible"}


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def post_reset_password(
    payload: ResetPasswordRequest, session: SessionDep
) -> None:
    try:
        await reset_password(
            session, raw_token=payload.token, new_password=payload.new_password
        )
    except OneTimeTokenInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "error": "token_invalid",
                "message": "Ссылка недействительна или истекла.",
            },
        ) from exc


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_endpoint(
    payload: DeleteAccountRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    try:
        await delete_account(
            session, user=user, password_confirmation=payload.password
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "invalid_credentials",
                "message": "Неверный пароль.",
            },
        ) from exc
