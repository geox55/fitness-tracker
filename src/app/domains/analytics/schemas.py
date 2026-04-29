from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class OverviewMetrics(BaseModel):
    workouts_this_month: int
    total_weight_kg: int
    total_weight_delta_percent: int
    active_streak_days: int
    streak_is_personal_best: bool


class StrengthPoint(BaseModel):
    day_offset: int  # дни от начала окна (0..30)
    weight_kg: float


class StrengthProgress(BaseModel):
    exercise_title: str | None
    current_max_kg: int
    points: list[StrengthPoint]


class RecentWorkoutItem(BaseModel):
    id: UUID
    performed_at: datetime
    day_label: str
    title: str
    sets: int
    reps: int
    weight_kg: int
    kind: str  # full_body | push | legs | pull | cardio | other


class OverviewResponse(BaseModel):
    month: date  # первый день месяца
    metrics: OverviewMetrics
    strength: StrengthProgress | None
    recent: list[RecentWorkoutItem]
