"""ORM-модели тренировочного плана — spec 006 §7.

Иерархия: `WorkoutPlan` → `PlanWeek (1..4)` → `PlanDay (1..7)` → `PlanExercise`.

Один `active` план на пользователя гарантируется на уровне БД через
частичный уникальный индекс (см. миграция 0014).

`input_features` хранит JSON-снапшот фичей, поданных в генератор —
для воспроизводимости (NFR-02) и оффлайн-анализа (REQ-15). PII туда не
кладём — только числовые/категориальные фичи (NFR-04).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...db import Base

PlanStatus = Literal["active", "archived"]
DayType = Literal["strength", "cardio", "rest"]


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[PlanStatus] = mapped_column(String, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    # `valid_until` = generated_at + 4 недели (по спеке) — считается в сервисе.
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)

    goal: Mapped[str] = mapped_column(String, nullable=False)
    training_level: Mapped[str] = mapped_column(String, nullable=False)
    frequency: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # JSONB вместо JSON: дешевле индексировать/запрашивать частично, если
    # понадобится оффлайн-аналитика по фичам. PII здесь не хранится.
    input_features: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False)

    # `archived_at` нужен для истории планов; для active — NULL.
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    weeks: Mapped[list["PlanWeek"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="PlanWeek.week_no",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_workout_plans_status",
        ),
        CheckConstraint(
            "frequency BETWEEN 2 AND 6",
            name="ck_workout_plans_frequency",
        ),
    )


class PlanWeek(Base):
    __tablename__ = "plan_weeks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    plan: Mapped[WorkoutPlan] = relationship(back_populates="weeks")
    days: Mapped[list["PlanDay"]] = relationship(
        back_populates="week",
        cascade="all, delete-orphan",
        order_by="PlanDay.day_no",
    )

    __table_args__ = (
        UniqueConstraint("plan_id", "week_no", name="uq_plan_weeks_no"),
        CheckConstraint("week_no BETWEEN 1 AND 4", name="ck_plan_weeks_no"),
    )


class PlanDay(Base):
    __tablename__ = "plan_days"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    week_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plan_weeks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[DayType] = mapped_column(String, nullable=False)

    week: Mapped[PlanWeek] = relationship(back_populates="days")
    exercises: Mapped[list["PlanExercise"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
        order_by="PlanExercise.order_no",
    )

    __table_args__ = (
        UniqueConstraint("week_id", "day_no", name="uq_plan_days_no"),
        CheckConstraint("day_no BETWEEN 1 AND 7", name="ck_plan_days_no"),
        CheckConstraint(
            "type IN ('strength','cardio','rest')",
            name="ck_plan_days_type",
        ),
    )


class PlanExercise(Base):
    __tablename__ = "plan_exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    day_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plan_days.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        nullable=False,
    )
    target_sets: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    target_reps_min: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    target_reps_max: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    target_rpe: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    day: Mapped[PlanDay] = relationship(back_populates="exercises")

    __table_args__ = (
        UniqueConstraint("day_id", "order_no", name="uq_plan_exercises_order"),
        CheckConstraint(
            "target_sets BETWEEN 1 AND 10",
            name="ck_plan_exercises_sets",
        ),
        CheckConstraint(
            "target_reps_min BETWEEN 1 AND 50",
            name="ck_plan_exercises_reps_min",
        ),
        CheckConstraint(
            "target_reps_max BETWEEN target_reps_min AND 50",
            name="ck_plan_exercises_reps_max",
        ),
        CheckConstraint(
            "target_rpe IS NULL OR target_rpe BETWEEN 5 AND 10",
            name="ck_plan_exercises_rpe",
        ),
        CheckConstraint(
            "rest_seconds IS NULL OR rest_seconds BETWEEN 30 AND 600",
            name="ck_plan_exercises_rest",
        ),
    )
