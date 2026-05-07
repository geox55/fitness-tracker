"""inbody_forecasts + forecast_evaluations — spec 008.

Revision ID: 0008_forecast
Revises: 0007_notifications
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_forecast"
down_revision: str | None = "0007_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inbody_forecasts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "based_on_inbody_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inbody_measurements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("horizon_weeks", sa.SmallInteger(), nullable=False),
        sa.Column("target_metric", sa.String(), nullable=False),
        sa.Column("point_estimate", sa.Numeric(6, 2), nullable=False),
        sa.Column("ci_low", sa.Numeric(6, 2), nullable=False),
        sa.Column("ci_high", sa.Numeric(6, 2), nullable=False),
        sa.Column("confidence", sa.String(), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column(
            "input_features",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "fallback",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "what_if",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("interpretation", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "horizon_weeks IN (1, 2, 4)", name="ck_forecast_horizon"
        ),
        sa.CheckConstraint(
            "target_metric IN ('weight_kg','body_fat_percent','muscle_mass_kg')",
            name="ck_forecast_target",
        ),
        sa.CheckConstraint(
            "confidence IN ('high','medium','low')",
            name="ck_forecast_confidence",
        ),
        sa.CheckConstraint("ci_low <= point_estimate", name="ck_forecast_ci_low"),
        sa.CheckConstraint(
            "ci_high >= point_estimate", name="ck_forecast_ci_high"
        ),
        sa.UniqueConstraint(
            "user_id",
            "generated_at",
            "target_metric",
            "horizon_weeks",
            "what_if",
            name="uq_forecast_batch_point",
        ),
    )
    op.create_index(
        "ix_forecast_user_generated",
        "inbody_forecasts",
        ["user_id", "generated_at"],
    )

    op.create_table(
        "forecast_evaluations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "forecast_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inbody_forecasts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "actual_inbody_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inbody_measurements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("absolute_error", sa.Numeric(6, 2), nullable=False),
        sa.Column("within_ci", sa.Boolean(), nullable=False),
        sa.Column(
            "evaluated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("forecast_evaluations")
    op.drop_index("ix_forecast_user_generated", table_name="inbody_forecasts")
    op.drop_table("inbody_forecasts")
