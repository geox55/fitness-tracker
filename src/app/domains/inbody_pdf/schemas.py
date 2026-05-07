"""Pydantic-схемы PDF-импорта — spec 013 §9."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ...domains.inbody.schemas import CreateMeasurementRequest, MeasurementRead

JobStatus = Literal[
    "parsing",
    "ready",
    "partial",
    "failed",
    "not_inbody",
    "encrypted",
    "scanned_unsupported",
]


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: JobStatus
    template: str | None
    extracted: dict[str, Any]
    confidence: dict[str, Any]
    missing_fields: list[str]
    error_message: str | None
    created_at: datetime
    confirmed_at: datetime | None


class ConfirmRequest(BaseModel):
    """Поле-за-полем пользовательские правки + дата измерения.

    `measured_at` обязательно — пользователь должен подтвердить либо ту
    дату, что напечатана в PDF, либо текущую (если в отчёте даты нет).
    Поэтому используем тот же CreateMeasurementRequest как «канвас»,
    но все поля делаем опциональными — дёргаем лишь то, что хочет
    переопределить пользователь (REQ-04 spec 013 / Scenario превью).
    """

    model_config = ConfigDict(extra="forbid")

    # Берём схему manual-ввода и делаем все поля опциональными:
    # пользователь может просто подтвердить распознанное.
    measured_at: datetime | None = None
    overrides: dict[str, Any] | None = None


class ConfirmResponse(BaseModel):
    measurement: MeasurementRead


# Реэкспорт чтобы FastAPI mount-ы видели одну схему запроса для manual-ввода
# (например, для UI, генерирующего форму превью на основе схемы InBody).
__all__ = [
    "ConfirmRequest",
    "ConfirmResponse",
    "CreateMeasurementRequest",
    "JobRead",
    "JobStatus",
]
