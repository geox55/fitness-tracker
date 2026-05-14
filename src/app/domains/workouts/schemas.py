from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StartWorkoutRequest(BaseModel):
    origin: Literal["plan", "freestyle"] = "freestyle"
    notes: str | None = Field(default=None, max_length=500)


class WorkoutPatch(BaseModel):
    """PATCH /workouts/{id}. Все поля опциональны.

    Pydantic не различает «поле не передано» и «передано null» по типу — этим
    занимается `model_dump(exclude_unset=True)` в route-handler'е. Для дат
    null означает «оставить как есть» (сбросить performed_at нельзя — без него
    тренировка теряет смысл).
    """

    notes: str | None = Field(default=None, max_length=500)
    performed_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)


class LogSetRequest(BaseModel):
    exercise_id: UUID
    set_number: int = Field(ge=1, le=20)
    reps: int = Field(ge=1, le=200)
    weight_kg: float = Field(ge=0, le=500)
    rpe: int | None = Field(default=None, ge=1, le=10)
    rest_seconds: int | None = Field(default=None, ge=0, le=1800)


class ExerciseLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exercise_id: UUID
    set_number: int
    reps: int
    weight_kg: float
    rpe: int | None
    rest_seconds: int | None
    skipped: bool
    logged_at: datetime


class WorkoutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    performed_at: datetime
    finished_at: datetime | None
    status: str
    origin: str
    notes: str | None
    logs: list[ExerciseLogRead] = []


class WorkoutSummary(BaseModel):
    """Сжатая запись для списка истории."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    performed_at: datetime
    finished_at: datetime | None
    status: str
    origin: str
    sets_count: int = 0
    total_tonnage: float = 0.0


class WorkoutListResponse(BaseModel):
    items: list[WorkoutSummary]
    total: int
