"""workouts: plan_day_id — связь с PlanDay (spec 005 REQ-12).

Делаем поле nullable + ON DELETE SET NULL: если план архивируется и
позже физически удаляется, история тренировок не теряется — просто
теряется обратная ссылка.

Revision ID: 0015_workouts_plan_day_id
Revises: 0014_workout_plans
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0015_workouts_plan_day_id"
down_revision: str | None = "0014_workout_plans"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "workouts",
        sa.Column(
            "plan_day_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plan_days.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_workouts_plan_day_id",
        "workouts",
        ["plan_day_id"],
        postgresql_where=sa.text("plan_day_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_workouts_plan_day_id", table_name="workouts")
    op.drop_column("workouts", "plan_day_id")
