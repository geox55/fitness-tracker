"""SQLAlchemy ORM модель InBodyMeasurement — spec 003.

Append-only: запись нельзя редактировать после создания (REQ-07). Удаление —
hard-delete с подтверждением, см. сервис.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base

Source = Literal["manual", "pdf"]
Sex = Literal["male", "female"]


class InBodyMeasurement(Base):
    __tablename__ = "inbody_measurements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Снапшоты на момент измерения (REQ data model)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    height_cm: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    sex: Mapped[Sex] = mapped_column(String, nullable=False)

    body_fat_percent: Mapped[Decimal] = mapped_column(
        Numeric(4, 1), nullable=False
    )
    muscle_mass_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    body_water_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1), nullable=True
    )
    protein_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2), nullable=True
    )
    minerals_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2), nullable=True
    )
    visceral_fat_level: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    bmr_kcal: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    fat_free_mass_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    bmi: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)

    source: Mapped[Source] = mapped_column(String, nullable=False)
    # Storage-key оригинального PDF (для source='pdf'). Сам URL — signed,
    # выдаётся API на лету через storage.signed_url (NFR-04 spec 013).
    original_pdf_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("weight_kg BETWEEN 30 AND 300", name="ck_inbody_weight"),
        CheckConstraint("height_cm BETWEEN 100 AND 250", name="ck_inbody_height"),
        CheckConstraint("sex IN ('male','female')", name="ck_inbody_sex"),
        CheckConstraint(
            "body_fat_percent BETWEEN 1 AND 70", name="ck_inbody_body_fat"
        ),
        CheckConstraint(
            "muscle_mass_kg IS NULL OR muscle_mass_kg BETWEEN 5 AND 120",
            name="ck_inbody_muscle_mass",
        ),
        CheckConstraint(
            "body_water_percent IS NULL OR body_water_percent BETWEEN 30 AND 80",
            name="ck_inbody_water",
        ),
        CheckConstraint(
            "protein_kg IS NULL OR protein_kg BETWEEN 1 AND 30",
            name="ck_inbody_protein",
        ),
        CheckConstraint(
            "minerals_kg IS NULL OR minerals_kg BETWEEN 0.5 AND 10",
            name="ck_inbody_minerals",
        ),
        CheckConstraint(
            "visceral_fat_level IS NULL OR visceral_fat_level BETWEEN 1 AND 30",
            name="ck_inbody_visceral",
        ),
        CheckConstraint(
            "bmr_kcal IS NULL OR bmr_kcal BETWEEN 500 AND 5000",
            name="ck_inbody_bmr",
        ),
        CheckConstraint(
            "fat_free_mass_kg IS NULL OR fat_free_mass_kg BETWEEN 20 AND 200",
            name="ck_inbody_ffm",
        ),
        CheckConstraint("source IN ('manual','pdf')", name="ck_inbody_source"),
    )
