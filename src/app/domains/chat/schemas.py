"""Pydantic-схемы чата — spec 009 §9."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Author = Literal["user", "assistant"]
Source = Literal["scripted", "templated", "llm", "user"]


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author: Author
    content: str
    source: Source
    created_at: datetime


class PostMessageRequest(BaseModel):
    """Свободный текст или явный topic_id (нажатие quick-reply)."""

    model_config = ConfigDict(extra="forbid")

    content: Annotated[str, Field(min_length=1, max_length=4000)]
    topic_id: str | None = None


class PostMessageResponse(BaseModel):
    """Возвращаем пару: эхо пользователя + ответ ассистента."""

    user_message: ChatMessageRead
    assistant_message: ChatMessageRead


class MessageListResponse(BaseModel):
    items: list[ChatMessageRead]
    total: int


class QuickReply(BaseModel):
    id: str
    text: str


class QuickRepliesResponse(BaseModel):
    items: list[QuickReply]
    llm_enabled: bool
