from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

Source = Literal["manual", "pdf"]
Sex = Literal["male", "female"]

WeightKg = Annotated[float, Field(ge=30, le=300)]
HeightCm = Annotated[float, Field(ge=100, le=250)]
BodyFatPercent = Annotated[float, Field(ge=1, le=70)]
MuscleMassKg = Annotated[float, Field(ge=5, le=120)]
BodyWaterPercent = Annotated[float, Field(ge=30, le=80)]
ProteinKg = Annotated[float, Field(ge=1, le=30)]
MineralsKg = Annotated[float, Field(ge=0.5, le=10)]
VisceralFatLevel = Annotated[int, Field(ge=1, le=30)]
BmrKcal = Annotated[int, Field(ge=500, le=5000)]
FatFreeMassKg = Annotated[float, Field(ge=20, le=200)]


class CreateMeasurementRequest(BaseModel):
    """Ручной ввод. Дата измерения обязательна и должна быть ≤ now (REQ-01)."""

    model_config = ConfigDict(extra="forbid")

    measured_at: datetime
    weight_kg: WeightKg
    body_fat_percent: BodyFatPercent

    # Снапшот роста/пола: либо передан явно, либо подтянется из профиля сервисом.
    height_cm: HeightCm | None = None
    sex: Sex | None = None

    muscle_mass_kg: MuscleMassKg | None = None
    body_water_percent: BodyWaterPercent | None = None
    protein_kg: ProteinKg | None = None
    minerals_kg: MineralsKg | None = None
    visceral_fat_level: VisceralFatLevel | None = None
    bmr_kcal: BmrKcal | None = None
    fat_free_mass_kg: FatFreeMassKg | None = None

    @field_validator("measured_at")
    @classmethod
    def _no_future(cls, v: datetime) -> datetime:
        compare = v if v.tzinfo is not None else v.replace(tzinfo=UTC)
        if compare > datetime.now(UTC):
            raise ValueError("measured_at cannot be in the future")
        return v


class MeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    measured_at: datetime
    weight_kg: float
    height_cm: float
    sex: Sex
    body_fat_percent: float
    muscle_mass_kg: float | None
    body_water_percent: float | None
    protein_kg: float | None
    minerals_kg: float | None
    visceral_fat_level: int | None
    bmr_kcal: int | None
    fat_free_mass_kg: float | None
    bmi: float
    source: Source
    original_pdf_url: str | None
    created_at: datetime


class MeasurementListResponse(BaseModel):
    items: list[MeasurementRead]
    total: int
