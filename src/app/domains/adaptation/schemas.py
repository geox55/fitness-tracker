"""Pydantic-схемы adaptation — spec 009."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Trigger = Literal[
    "weight_change",
    "goal_change",
    "frequency_change",
    "cycle_end",
    "manual",
]
TargetPlan = Literal["workout", "nutrition", "both"]
Status = Literal["pending", "auto_applied", "user_confirmed", "dismissed"]


class PlanRebuildEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trigger: Trigger
    target_plan: TargetPlan
    status: Status
    delta_kg: float | None
    delta_percent: float | None
    triggered_at: datetime
    applied_at: datetime | None


class PlanRebuildEventList(BaseModel):
    items: list[PlanRebuildEventRead]
    total: int


class RebuildPlanRequest(BaseModel):
    """Пользователь подтверждает регенерацию (Scenario 2.2)."""

    model_config = ConfigDict(extra="forbid")

    target: TargetPlan = Field(default="both")


class RebuildPlanResponse(BaseModel):
    # Scenario 2.2 говорит «старые планы архивируются, новые генерируются».
    # Сама генерация плана идёт в specs 006/007, которые ещё не реализованы.
    # Возвращаем подтверждение события для UI и идентификатор для трекинга.
    event_id: UUID
    target_plan: TargetPlan
    status: Status
    detail: str
