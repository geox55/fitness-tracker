"""workouts + exercise_logs — spec 005."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_workouts"
down_revision: str | None = "0002_exercises"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workouts",
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
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('in_progress','completed','auto_finished','cancelled')",
            name="ck_workouts_status",
        ),
        sa.CheckConstraint(
            "origin IN ('plan','freestyle')", name="ck_workouts_origin"
        ),
    )
    op.create_index(
        "ix_workouts_user_performed", "workouts", ["user_id", "performed_at"]
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ux_workouts_active_per_user
        ON workouts (user_id) WHERE status = 'in_progress'
        """
    )

    op.create_table(
        "exercise_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "workout_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workouts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exercise_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercises.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("set_number", sa.SmallInteger(), nullable=False),
        sa.Column("reps", sa.SmallInteger(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=False),
        sa.Column("rpe", sa.SmallInteger(), nullable=True),
        sa.Column("rest_seconds", sa.SmallInteger(), nullable=True),
        sa.Column(
            "skipped",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "logged_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "workout_id",
            "exercise_id",
            "set_number",
            name="uq_exercise_logs_set",
        ),
        sa.CheckConstraint("set_number >= 1", name="ck_exercise_logs_set_number"),
        sa.CheckConstraint("reps BETWEEN 1 AND 200", name="ck_exercise_logs_reps"),
        sa.CheckConstraint(
            "weight_kg BETWEEN 0 AND 500", name="ck_exercise_logs_weight"
        ),
        sa.CheckConstraint(
            "rpe IS NULL OR rpe BETWEEN 1 AND 10", name="ck_exercise_logs_rpe"
        ),
    )
    op.create_index(
        "ix_exercise_logs_exercise_logged",
        "exercise_logs",
        ["exercise_id", "logged_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_exercise_logs_exercise_logged", table_name="exercise_logs")
    op.drop_table("exercise_logs")
    op.execute("DROP INDEX IF EXISTS ux_workouts_active_per_user")
    op.drop_index("ix_workouts_user_performed", table_name="workouts")
    op.drop_table("workouts")
