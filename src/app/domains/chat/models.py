"""ChatMessage — spec 009 §6.

Immutable: запись нельзя редактировать, только удалить вместе с пользователем
(GDPR, Edge case §10).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base

Author = Literal["user", "assistant"]
Source = Literal["scripted", "templated", "llm", "user"]


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    author: Mapped[Author] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Source] = mapped_column(String, nullable=False)
    # Снапшот данных, использованных при шаблонизации — для отладки и
    # воспроизводимости (NFR-04 говорит про PII; здесь только agg-данные).
    context: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "author IN ('user','assistant')", name="ck_chat_author"
        ),
        CheckConstraint(
            "source IN ('scripted','templated','llm','user')",
            name="ck_chat_source",
        ),
        # Контент ≤4000 chars — REQ data model.
        CheckConstraint("char_length(content) <= 4000", name="ck_chat_content_len"),
        Index("ix_chat_user_created", "user_id", "created_at"),
    )
