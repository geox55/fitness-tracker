"""SQLAlchemy ORM модели прогноза InBody — spec 008.

`InBodyForecast` — одна строка на (user, generated_at, target_metric, horizon),
храним каждую точку прогноза отдельно: упрощает SQL для дашборда модели и
сравнения с фактом по горизонту (Scenario 3).

`ForecastEvaluation` — оценка качества прогноза, проставляется когда приходит
новый InBody через ~T+horizon. Используется для метрик MAE/coverage (SC-01..04).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
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

TargetMetric = Literal["weight_kg", "body_fat_percent", "muscle_mass_kg"]
Confidence = Literal["high", "medium", "low"]


class InBodyForecast(Base):
    __tablename__ = "inbody_forecasts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    based_on_inbody_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inbody_measurements.id", ondelete="CASCADE"),
        nullable=False,
    )
    horizon_weeks: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    target_metric: Mapped[TargetMetric] = mapped_column(String, nullable=False)

    point_estimate: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    ci_low: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    ci_high: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    confidence: Mapped[Confidence] = mapped_column(String, nullable=False)

    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    # Анонимизированный slate фичей, на которых построили прогноз — для
    # reproducibility (NFR-04) и последующего дообучения.
    input_features: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    fallback: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", default=False
    )
    what_if: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", default=False
    )
    interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)

    evaluation: Mapped[ForecastEvaluation | None] = relationship(
        back_populates="forecast",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "horizon_weeks IN (1, 2, 4)", name="ck_forecast_horizon"
        ),
        CheckConstraint(
            "target_metric IN ('weight_kg','body_fat_percent','muscle_mass_kg')",
            name="ck_forecast_target",
        ),
        CheckConstraint(
            "confidence IN ('high','medium','low')", name="ck_forecast_confidence"
        ),
        CheckConstraint("ci_low <= point_estimate", name="ck_forecast_ci_low"),
        CheckConstraint(
            "ci_high >= point_estimate", name="ck_forecast_ci_high"
        ),
        # Один основной (не what_if) прогноз на (user, batch, target, horizon).
        # Batch здесь — generated_at; пара одинаковых батчей отличается по
        # generated_at, и в том же батче дубль (target, horizon) недопустим.
        Index(
            "ix_forecast_user_generated",
            "user_id",
            "generated_at",
        ),
        UniqueConstraint(
            "user_id",
            "generated_at",
            "target_metric",
            "horizon_weeks",
            "what_if",
            name="uq_forecast_batch_point",
        ),
    )


class ForecastEvaluation(Base):
    __tablename__ = "forecast_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    forecast_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inbody_forecasts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    actual_inbody_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inbody_measurements.id", ondelete="CASCADE"),
        nullable=False,
    )
    absolute_error: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    within_ci: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    forecast: Mapped[InBodyForecast] = relationship(back_populates="evaluation")
