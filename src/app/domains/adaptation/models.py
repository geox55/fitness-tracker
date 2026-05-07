"""PlanRebuildEvent — audit watcher'а адаптации (spec 009 §6)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base

Trigger = Literal[
    "weight_change",
    "goal_change",
    "frequency_change",
    "cycle_end",
    "manual",
]
TargetPlan = Literal["workout", "nutrition", "both"]
Status = Literal["pending", "auto_applied", "user_confirmed", "dismissed"]


class PlanRebuildEvent(Base):
    __tablename__ = "plan_rebuild_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    trigger: Mapped[Trigger] = mapped_column(String, nullable=False)
    target_plan: Mapped[TargetPlan] = mapped_column(String, nullable=False)
    status: Mapped[Status] = mapped_column(
        String, nullable=False, server_default="pending"
    )
    # Сохраняем ключевые числа триггера, чтобы потом сравнить с фактом и
    # понять, насколько часто мы корректно ловим заметные изменения веса
    # (метрика для дипломной работы).
    delta_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    delta_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "trigger IN ('weight_change','goal_change','frequency_change',"
            "'cycle_end','manual')",
            name="ck_rebuild_trigger",
        ),
        CheckConstraint(
            "target_plan IN ('workout','nutrition','both')",
            name="ck_rebuild_target",
        ),
        CheckConstraint(
            "status IN ('pending','auto_applied','user_confirmed','dismissed')",
            name="ck_rebuild_status",
        ),
        Index("ix_rebuild_user_status", "user_id", "status", "triggered_at"),
    )
