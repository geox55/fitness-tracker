"""workout_plans + plan_weeks + plan_days + plan_exercises — spec 006 §7.

Иерархия плана:
    workout_plans
        plan_weeks (week_no 1..4)
            plan_days (day_no 1..7, type strength/cardio/rest)
                plan_exercises (FK exercises.id)

Один active план на пользователя гарантируем частичным уникальным
индексом по `user_id WHERE status = 'active'`.

Revision ID: 0014_workout_plans
Revises: 0013_pdf_export
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014_workout_plans"
down_revision: str | None = "0013_pdf_export"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workout_plans",
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
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("valid_until", sa.Date(), nullable=False),
        sa.Column("goal", sa.String(), nullable=False),
        sa.Column("training_level", sa.String(), nullable=False),
        sa.Column("frequency", sa.SmallInteger(), nullable=False),
        sa.Column(
            "input_features",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("model_version", sa.String(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('active','archived')",
            name="ck_workout_plans_status",
        ),
        sa.CheckConstraint(
            "frequency BETWEEN 2 AND 6",
            name="ck_workout_plans_frequency",
        ),
    )
    op.create_index(
        "ix_workout_plans_user_id",
        "workout_plans",
        ["user_id"],
    )
    # Один active план на пользователя (REQ-13 spec 006).
    op.create_index(
        "uq_workout_plans_one_active",
        "workout_plans",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "plan_weeks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workout_plans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("week_no", sa.SmallInteger(), nullable=False),
        sa.UniqueConstraint("plan_id", "week_no", name="uq_plan_weeks_no"),
        sa.CheckConstraint(
            "week_no BETWEEN 1 AND 4", name="ck_plan_weeks_no"
        ),
    )
    op.create_index("ix_plan_weeks_plan_id", "plan_weeks", ["plan_id"])

    op.create_table(
        "plan_days",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "week_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plan_weeks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("day_no", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.UniqueConstraint("week_id", "day_no", name="uq_plan_days_no"),
        sa.CheckConstraint(
            "day_no BETWEEN 1 AND 7", name="ck_plan_days_no"
        ),
        sa.CheckConstraint(
            "type IN ('strength','cardio','rest')",
            name="ck_plan_days_type",
        ),
    )
    op.create_index("ix_plan_days_week_id", "plan_days", ["week_id"])

    op.create_table(
        "plan_exercises",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "day_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plan_days.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("order_no", sa.SmallInteger(), nullable=False),
        sa.Column(
            "exercise_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercises.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("target_sets", sa.SmallInteger(), nullable=False),
        sa.Column("target_reps_min", sa.SmallInteger(), nullable=False),
        sa.Column("target_reps_max", sa.SmallInteger(), nullable=False),
        sa.Column("target_rpe", sa.SmallInteger(), nullable=True),
        sa.Column("rest_seconds", sa.Integer(), nullable=True),
        sa.Column("target_weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "day_id", "order_no", name="uq_plan_exercises_order"
        ),
        sa.CheckConstraint(
            "target_sets BETWEEN 1 AND 10",
            name="ck_plan_exercises_sets",
        ),
        sa.CheckConstraint(
            "target_reps_min BETWEEN 1 AND 50",
            name="ck_plan_exercises_reps_min",
        ),
        sa.CheckConstraint(
            "target_reps_max BETWEEN target_reps_min AND 50",
            name="ck_plan_exercises_reps_max",
        ),
        sa.CheckConstraint(
            "target_rpe IS NULL OR target_rpe BETWEEN 5 AND 10",
            name="ck_plan_exercises_rpe",
        ),
        sa.CheckConstraint(
            "rest_seconds IS NULL OR rest_seconds BETWEEN 30 AND 600",
            name="ck_plan_exercises_rest",
        ),
    )
    op.create_index(
        "ix_plan_exercises_day_id", "plan_exercises", ["day_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_plan_exercises_day_id", table_name="plan_exercises")
    op.drop_table("plan_exercises")
    op.drop_index("ix_plan_days_week_id", table_name="plan_days")
    op.drop_table("plan_days")
    op.drop_index("ix_plan_weeks_plan_id", table_name="plan_weeks")
    op.drop_table("plan_weeks")
    op.drop_index(
        "uq_workout_plans_one_active", table_name="workout_plans"
    )
    op.drop_index("ix_workout_plans_user_id", table_name="workout_plans")
    op.drop_table("workout_plans")
