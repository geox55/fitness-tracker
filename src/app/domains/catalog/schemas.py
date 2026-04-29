from uuid import UUID

from pydantic import BaseModel, ConfigDict


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


class ExerciseDetail(ExerciseSummary):
    instructions: str
    calories_burned_per_hour: float | None


class ExerciseListResponse(BaseModel):
    items: list[ExerciseSummary]
    total: int
