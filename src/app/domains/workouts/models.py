import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...db import Base

WorkoutStatus = Literal["in_progress", "completed", "auto_finished", "cancelled"]
WorkoutOrigin = Literal["plan", "freestyle"]


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[WorkoutStatus] = mapped_column(String, nullable=False)
    origin: Mapped[WorkoutOrigin] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    logs: Mapped[list["ExerciseLog"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress','completed','auto_finished','cancelled')",
            name="ck_workouts_status",
        ),
        CheckConstraint(
            "origin IN ('plan','freestyle')", name="ck_workouts_origin"
        ),
    )


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        nullable=False,
    )
    set_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reps: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    rpe: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    skipped: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    workout: Mapped[Workout] = relationship(back_populates="logs")

    __table_args__ = (
        UniqueConstraint(
            "workout_id", "exercise_id", "set_number", name="uq_exercise_logs_set"
        ),
        CheckConstraint("set_number >= 1", name="ck_exercise_logs_set_number"),
        CheckConstraint("reps BETWEEN 1 AND 200", name="ck_exercise_logs_reps"),
        CheckConstraint(
            "weight_kg BETWEEN 0 AND 500", name="ck_exercise_logs_weight"
        ),
        CheckConstraint(
            "rpe IS NULL OR rpe BETWEEN 1 AND 10", name="ck_exercise_logs_rpe"
        ),
    )
