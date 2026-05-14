from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExerciseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exercise_id: str
    exercise_name: str
    exercise_name_ru: str | None
    primary_muscle_group: str
    secondary_muscle_group: list[str]
    equipment: list[str]
    body_region: str
    # Spec 014: проставляются эндпойнтом per-user; в чистом ORM-объекте полей
    # нет, поэтому даём дефолты — model_validate без них не падает.
    is_favorite: bool = False
    is_mine: bool = False


class ExerciseDetail(ExerciseSummary):
    instructions: str
    calories_burned_per_hour: float | None


class ExerciseListResponse(BaseModel):
    items: list[ExerciseSummary]
    total: int


# --- Создание / редактирование пользовательских упражнений ----------------

# Spec 014 §2: пользовательские поля минимальны. Остальное (instructions,
# calories) можно добавить позже без миграции — поля на модели уже есть.


class _ExerciseEditableFields(BaseModel):
    """Общая основа для create/update — DRY и единая валидация."""

    exercise_name: str = Field(min_length=1, max_length=200)
    exercise_name_ru: str | None = Field(default=None, max_length=200)
    primary_muscle_group: str = Field(min_length=1, max_length=40)
    secondary_muscle_group: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    body_region: str = Field(min_length=1, max_length=40)


class ExerciseCreateRequest(_ExerciseEditableFields):
    pass


class ExerciseUpdateRequest(BaseModel):
    """PATCH — все поля опциональны. exclude_unset на стороне эндпойнта."""

    exercise_name: str | None = Field(default=None, min_length=1, max_length=200)
    exercise_name_ru: str | None = Field(default=None, max_length=200)
    primary_muscle_group: str | None = Field(default=None, min_length=1, max_length=40)
    secondary_muscle_group: list[str] | None = None
    equipment: list[str] | None = None
    body_region: str | None = Field(default=None, min_length=1, max_length=40)
