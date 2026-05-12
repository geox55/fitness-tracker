"""Pydantic-схемы API плана — spec 006 §9."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Goal = Literal["weight_loss", "muscle_gain", "maintenance"]
Level = Literal["beginner", "intermediate", "advanced"]
PlanStatus = Literal["active", "archived"]
DayType = Literal["strength", "cardio", "rest"]


class PlanGenerateOverride(BaseModel):
    """Override-параметры для POST /plans/generate (spec 006 §9).

    Если поле None — берём значение из профиля (REQ-04/05) или дефолт
    для equipment_available (см. сервис).
    """

    model_config = ConfigDict(extra="forbid")

    training_frequency: int | None = Field(default=None, ge=2, le=6)
    equipment_available: list[str] | None = None
    # Цель/уровень тоже можно переопределить — пригодится для «что-если»
    # сценариев («а если я перешёл на cutting?»). Профиль не меняется.
    goal: Goal | None = None
    training_level: Level | None = None


class PlanGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    override: PlanGenerateOverride | None = None


class PlanExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exercise_id: uuid.UUID | None  # None для cardio (нет каталожного упражнения)
    exercise_name: str
    order_no: int
    target_sets: int
    target_reps_min: int
    target_reps_max: int
    target_rpe: int | None
    rest_seconds: int | None
    target_weight_kg: float | None
    notes: str | None


class PlanDayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    day_no: int
    name: str
    type: DayType
    exercises: list[PlanExerciseRead]


class PlanWeekRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    week_no: int
    days: list[PlanDayRead]


class PlanRead(BaseModel):
    """Полный план: 4 недели × дни × упражнения. Spec 006 §9 response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: PlanStatus
    generated_at: datetime
    valid_until: date
    goal: Goal
    training_level: Level
    frequency: int
    model_version: str
    weeks: list[PlanWeekRead]
    warnings: list[str] = []


class PlanSummary(BaseModel):
    """Краткая карточка плана для GET /plans?status=archived."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: PlanStatus
    generated_at: datetime
    valid_until: date
    goal: Goal
    training_level: Level
    frequency: int
    model_version: str


class PlanListResponse(BaseModel):
    items: list[PlanSummary]
    total: int
