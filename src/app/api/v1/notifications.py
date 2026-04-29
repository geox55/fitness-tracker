"""Notifications endpoints — spec 011 (inbox + preferences)."""

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from ...domains.notifications.schemas import (
    InboxItem,
    InboxResponse,
    PreferencesRead,
    PreferencesUpdate,
)
from ...domains.notifications.service import (
    delete_notification,
    get_or_create_preferences,
    list_inbox,
    mark_read,
    update_preferences,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/preferences", response_model=PreferencesRead)
async def get_preferences(
    user: CurrentUserDep, session: SessionDep
) -> PreferencesRead:
    prefs = await get_or_create_preferences(session, user_id=user.id)
    return PreferencesRead.model_validate(prefs)


@router.patch("/preferences", response_model=PreferencesRead)
async def patch_preferences(
    payload: PreferencesUpdate,
    user: CurrentUserDep,
    session: SessionDep,
) -> PreferencesRead:
    changes = payload.model_dump(exclude_unset=True)
    prefs = await update_preferences(
        session, user_id=user.id, changes=changes
    )
    return PreferencesRead.model_validate(prefs)


@router.get("/inbox", response_model=InboxResponse)
async def inbox(
    user: CurrentUserDep,
    session: SessionDep,
    unread: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> InboxResponse:
    items, unread_count, total = await list_inbox(
        session,
        user_id=user.id,
        unread_only=unread,
        limit=limit,
        offset=offset,
    )
    return InboxResponse(
        items=[InboxItem.model_validate(i) for i in items],
        unread_count=unread_count,
        total=total,
    )


@router.post(
    "/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT
)
async def post_read(
    notification_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    item = await mark_read(
        session, user_id=user.id, notification_id=notification_id
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Сообщение не найдено"},
        )


@router.delete(
    "/{notification_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_one(
    notification_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    deleted = await delete_notification(
        session, user_id=user.id, notification_id=notification_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Сообщение не найдено"},
        )
