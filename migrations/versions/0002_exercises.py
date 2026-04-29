"""exercises table — минимум полей для FK из workouts/plans.

Полная схема и сидинг каталога — spec 004 + 012.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_exercises"
down_revision: str | None = "0001_init"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exercises",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("exercise_id", sa.Text(), nullable=False),
        sa.Column("exercise_name", sa.Text(), nullable=False),
        sa.Column("exercise_name_ru", sa.Text(), nullable=True),
        sa.Column("primary_muscle_group", sa.Text(), nullable=False),
        sa.Column(
            "secondary_muscle_group",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("instructions", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "equipment",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("calories_burned_per_hour", sa.Numeric(6, 2), nullable=True),
        sa.Column("body_region", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("exercise_id", name="uq_exercises_slug"),
        sa.CheckConstraint(
            "body_region IN ('upper','lower','core','full_body')",
            name="ck_exercises_body_region",
        ),
    )
    op.create_index("ix_exercises_primary", "exercises", ["primary_muscle_group"])


def downgrade() -> None:
    op.drop_index("ix_exercises_primary", table_name="exercises")
    op.drop_table("exercises")
