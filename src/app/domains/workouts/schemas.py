from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StartWorkoutRequest(BaseModel):
    origin: Literal["plan", "freestyle"] = "freestyle"
    notes: str | None = Field(default=None, max_length=500)
    # spec 005 REQ-12: запуск тренировки из конкретного дня плана.
    # Если передан — сервер проверяет принадлежность плана пользователю,
    # выставляет `origin='plan'` и линкует FK.
    plan_day_id: UUID | None = None
    # spec 015 REQ-01: идемпотентность offline-старта тренировки.
    client_id: UUID | None = None


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
    # spec 015 REQ-01: client_id для идемпотентного offline-лога подхода.
    client_id: UUID | None = None


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
    # spec 016: nullable, не-NULL → лог в составе суперсета (общий group_id
    # для всех логов группы в рамках одной тренировки).
    superset_group_id: UUID | None = None


class GroupSupersetRequest(BaseModel):
    """spec 016 REQ-03. Принимает 2..10 exercise_id из текущей тренировки,
    атомарно ставит общий superset_group_id всем их логам.

    Лимит 10 — практический потолок для гигантских сетов. Если у любого
    из переданных упражнений уже есть group_id, он переиспользуется
    (idempotency-friendly: drop-zone в UI просто шлёт все ID соседних
    групп, не разбираясь — сервер сам сольёт)."""

    model_config = ConfigDict(extra="forbid")

    exercise_ids: list[UUID] = Field(min_length=2, max_length=10)


class UngroupSupersetRequest(BaseModel):
    """spec 016 REQ-04. Принимает group_id, сбрасывает в NULL."""

    model_config = ConfigDict(extra="forbid")

    group_id: UUID


class SupersetMutationResponse(BaseModel):
    group_id: UUID | None = None
    logs_updated: int


class WorkoutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    performed_at: datetime
    finished_at: datetime | None
    status: str
    origin: str
    notes: str | None
    plan_day_id: UUID | None = None
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
