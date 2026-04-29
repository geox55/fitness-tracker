from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Sex = Literal["male", "female"]
Goal = Literal["weight_loss", "muscle_gain", "maintenance"]
TrainingLevel = Literal["beginner", "intermediate", "advanced"]

NameStr = Annotated[str, Field(min_length=1, max_length=50)]
HeightCm = Annotated[float, Field(ge=100, le=250)]
WeightKg = Annotated[float, Field(ge=30, le=300)]
TrainingFrequency = Annotated[int, Field(ge=2, le=6)]
Allergy = Annotated[str, Field(min_length=1, max_length=64)]


def _validate_birth_date(value: date) -> date:
    today = date.today()
    if value > today:
        raise ValueError("birth_date cannot be in the future")
    age = today.year - value.year - (
        (today.month, today.day) < (value.month, value.day)
    )
    if age < 14:
        raise ValueError("user must be at least 14 years old")
    if age > 100:
        raise ValueError("user age must be ≤100 years")
    return value


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: EmailStr
    name: str | None
    sex: Sex | None
    birth_date: date | None
    height_cm: float | None
    baseline_weight_kg: float | None
    goal: Goal | None
    training_level: TrainingLevel | None
    training_frequency: int | None
    allergies: list[str]
    photo_url: str | None
    bmr_kcal: int | None
    onboarding_completed_at: datetime | None
    plan_rebuild_required: bool
    updated_at: datetime


class ProfileUpdateRequest(BaseModel):
    """Все поля опциональны: PATCH-обновление любого подмножества."""

    model_config = ConfigDict(extra="forbid")

    name: NameStr | None = None
    sex: Sex | None = None
    birth_date: date | None = None
    height_cm: HeightCm | None = None
    baseline_weight_kg: WeightKg | None = None
    goal: Goal | None = None
    training_level: TrainingLevel | None = None
    training_frequency: TrainingFrequency | None = None
    allergies: list[Allergy] | None = None

    @field_validator("birth_date")
    @classmethod
    def _check_birth_date(cls, v: date | None) -> date | None:
        return None if v is None else _validate_birth_date(v)


class IncompleteProfileError(BaseModel):
    error: Literal["incomplete_profile"] = "incomplete_profile"
    message: str
    missing_fields: list[str]
