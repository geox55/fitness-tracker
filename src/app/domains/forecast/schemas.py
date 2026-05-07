"""Pydantic-схемы прогноза InBody — spec 008.

Возвращаем формат, описанный в §9 спеки: метрики сгруппированы по target_metric,
каждая — список точек по горизонтам.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TargetMetric = Literal["weight_kg", "body_fat_percent", "muscle_mass_kg"]
Confidence = Literal["high", "medium", "low"]
HorizonWeeks = Annotated[int, Field(ge=1, le=4)]
TrainingFrequency = Annotated[int, Field(ge=2, le=6)]


class ForecastPoint(BaseModel):
    horizon_weeks: int
    point: float
    ci_low: float
    ci_high: float


class ForecastMetrics(BaseModel):
    weight_kg: list[ForecastPoint]
    body_fat_percent: list[ForecastPoint]
    muscle_mass_kg: list[ForecastPoint]


class ForecastResponse(BaseModel):
    generated_at: datetime
    model_version: str
    based_on_inbody_id: UUID
    confidence: Confidence
    fallback: bool
    what_if: bool = False
    metrics: ForecastMetrics
    interpretation: str


class WhatIfOverride(BaseModel):
    """Переопределения для what-if (Scenario 4).

    Все поля опциональны; диапазоны валидируются здесь же — REQ-10/Scenario 4
    говорит, что некорректный override должен возвращать 400.
    """

    model_config = ConfigDict(extra="forbid")

    training_frequency: TrainingFrequency | None = None
    calories_offset_kcal: Annotated[int, Field(ge=-1000, le=1000)] | None = None


class WhatIfRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    horizons: list[HorizonWeeks] = Field(default_factory=lambda: [1, 2, 4])
    override: WhatIfOverride


class HistoryEvaluation(BaseModel):
    """Оценка прошлого прогноза, если факт уже пришёл (Scenario 3)."""

    actual_inbody_id: UUID
    absolute_error: float
    within_ci: bool
    evaluated_at: datetime


class HistoryItem(BaseModel):
    id: UUID
    generated_at: datetime
    based_on_inbody_id: UUID
    target_metric: TargetMetric
    horizon_weeks: int
    point: float
    ci_low: float
    ci_high: float
    confidence: Confidence
    model_version: str
    fallback: bool
    what_if: bool
    evaluation: HistoryEvaluation | None = None


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
