"""Chat endpoints — spec 009 §9."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from ...config import get_settings
from ...domain.chat.topics import TOPICS
from ...domains.chat.schemas import (
    ChatMessageRead,
    MessageListResponse,
    PostMessageRequest,
    PostMessageResponse,
    QuickRepliesResponse,
    QuickReply,
)
from ...domains.chat.service import (
    LLMUnavailableError,
    RateLimitedError,
    list_messages,
    post_message,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages", response_model=MessageListResponse)
async def get_messages(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
    before: Annotated[datetime | None, Query()] = None,
) -> MessageListResponse:
    items, total = await list_messages(
        session, user_id=user.id, limit=limit, before=before
    )
    return MessageListResponse(
        items=[ChatMessageRead.model_validate(m) for m in items],
        total=total,
    )


@router.post(
    "/messages",
    response_model=PostMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_chat_message(
    payload: PostMessageRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> PostMessageResponse:
    settings = get_settings()
    try:
        user_msg, asst_msg = await post_message(
            session,
            user_id=user.id,
            content=payload.content,
            topic_id=payload.topic_id,
            llm_enabled=settings.chat_llm_enabled,
            llm=None,  # MVP: LLM-клиент не сконфигурирован
        )
    except RateLimitedError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limited",
                "message": "Слишком много сообщений. Подождите немного.",
            },
        ) from exc
    except LLMUnavailableError as exc:
        # spec 009 §9: 503 если LLM недоступен и скрипт не нашёл ответа.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "llm_unavailable",
                "message": "Свободные вопросы временно недоступны. Выберите тему.",
            },
        ) from exc

    return PostMessageResponse(
        user_message=ChatMessageRead.model_validate(user_msg),
        assistant_message=ChatMessageRead.model_validate(asst_msg),
    )


@router.get("/quick-replies", response_model=QuickRepliesResponse)
async def get_quick_replies(_user: CurrentUserDep) -> QuickRepliesResponse:
    settings = get_settings()
    return QuickRepliesResponse(
        items=[QuickReply(id=t.id, text=t.quick_reply) for t in TOPICS],
        llm_enabled=settings.chat_llm_enabled,
    )
