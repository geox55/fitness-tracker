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
# В MVP адаптируем только план тренировок (см. spec 009 Data Model).
TargetPlan = Literal["workout"]
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

    target: TargetPlan = Field(default="workout")


class RebuildPlanResponse(BaseModel):
    """Scenario 2.2 — `confirm_rebuild` запустил спека-006-генератор.

    Возвращаем id события (для аудита/трекинга), id свежего плана (UI
    сделает push на экран плана) и его warnings (composer может пометить,
    что замеров InBody нет — баннер на экране плана).
    """

    event_id: UUID
    target_plan: TargetPlan
    status: Status
    plan_id: UUID
    warnings: list[str] = Field(default_factory=list)
