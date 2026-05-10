"""SQLAlchemy ORM модель UserProfile — spec 002."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base

Sex = Literal["male", "female"]
Goal = Literal["weight_loss", "muscle_gain", "maintenance"]
TrainingLevel = Literal["beginner", "intermediate", "advanced"]


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sex: Mapped[Sex | None] = mapped_column(String, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1), nullable=True)
    baseline_weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    goal: Mapped[Goal | None] = mapped_column(String, nullable=True)
    # Целевые значения для прогресс-бара (REQ-06 spec 010). Без них раздел
    # «Прогресс по цели» отдаёт CTA «Укажите цель в профиле».
    target_weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    target_muscle_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    # Старт работы над целью — нужен, чтобы start_value брался не из
    # baseline_weight_kg, а из замера на этот момент: при смене цели в
    # середине процесса baseline уже не отражает реальный «старт».
    goal_started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    training_level: Mapped[TrainingLevel | None] = mapped_column(String, nullable=True)
    training_frequency: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    allergies: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bmr_kcal: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    plan_rebuild_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "sex IS NULL OR sex IN ('male','female')",
            name="ck_user_profiles_sex",
        ),
        CheckConstraint(
            "goal IS NULL OR goal IN ('weight_loss','muscle_gain','maintenance')",
            name="ck_user_profiles_goal",
        ),
        CheckConstraint(
            "training_level IS NULL OR "
            "training_level IN ('beginner','intermediate','advanced')",
            name="ck_user_profiles_training_level",
        ),
        CheckConstraint(
            "training_frequency IS NULL OR training_frequency BETWEEN 2 AND 6",
            name="ck_user_profiles_training_frequency",
        ),
        CheckConstraint(
            "height_cm IS NULL OR height_cm BETWEEN 100 AND 250",
            name="ck_user_profiles_height",
        ),
        CheckConstraint(
            "baseline_weight_kg IS NULL OR baseline_weight_kg BETWEEN 30 AND 300",
            name="ck_user_profiles_weight",
        ),
        CheckConstraint(
            "target_weight_kg IS NULL OR target_weight_kg BETWEEN 30 AND 300",
            name="ck_user_profiles_target_weight_kg",
        ),
        CheckConstraint(
            "target_muscle_kg IS NULL OR target_muscle_kg BETWEEN 5 AND 120",
            name="ck_user_profiles_target_muscle_kg",
        ),
    )
