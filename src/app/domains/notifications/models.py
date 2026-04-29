"""Модели уведомлений — spec 011.

NotificationPreferences — 1:1 с user, тоглы каналов и типов.
NotificationOutbox — лог всех отправок (in-app + email), один источник правды
для inbox и для аудита (REQ-11).
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base

NotificationType = Literal[
    "email_verify",
    "password_reset",
    "inbody_reminder",
    "plan_update",
    "weekly_summary",
]
Channel = Literal["email", "in_app"]
DeliveryStatus = Literal["queued", "sent", "failed", "bounced"]

# Только эти типы уважают пользовательские настройки. Transactional auth-типы
# отправляются всегда (REQ-08).
USER_CONTROLLED_TYPES: frozenset[str] = frozenset(
    {"inbody_reminder", "plan_update", "weekly_summary"}
)


class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    inbody_reminder: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    plan_update: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    weekly_summary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    email_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class NotificationOutbox(Base):
    __tablename__ = "notification_outbox"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[NotificationType] = mapped_column(String, nullable=False)
    channel: Mapped[Channel] = mapped_column(String, nullable=False)
    context_key: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    status: Mapped[DeliveryStatus] = mapped_column(
        String, nullable=False, default="queued", server_default="queued"
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('email_verify','password_reset','inbody_reminder',"
            "'plan_update','weekly_summary')",
            name="ck_notif_type",
        ),
        CheckConstraint(
            "channel IN ('email','in_app')", name="ck_notif_channel"
        ),
        CheckConstraint(
            "status IN ('queued','sent','failed','bounced')",
            name="ck_notif_status",
        ),
        CheckConstraint(
            "channel != 'in_app' OR sent_at IS NOT NULL",
            # in-app сообщение считается "доставленным" сразу при создании.
            name="ck_notif_in_app_sent",
        ),
    )
