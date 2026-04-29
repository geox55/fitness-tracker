"""FastAPI dependencies: общая инфраструктура для роутеров."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..domains.auth.models import User
from ..domains.auth.service import (
    UserNotFoundError,
    get_user_by_id,
    user_id_from_access_token,
)
from ..security import TokenInvalidError

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _extract_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Missing bearer token"},
        )
    return authorization[len("Bearer ") :].strip()


async def get_current_user(
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    token = _extract_bearer(authorization)
    try:
        user_id = await user_id_from_access_token(token)
        return await get_user_by_id(session, user_id)
    except TokenInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": str(exc)},
        ) from exc
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "User no longer exists"},
        ) from exc


CurrentUserDep = Annotated[User, Depends(get_current_user)]
