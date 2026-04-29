"""user_profiles — spec 002.

Revision ID: 0005_user_profile
Revises: 0004_seed_exercises
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_user_profile"
down_revision: str | None = "0004_seed_exercises"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(50), nullable=True),
        sa.Column("sex", sa.String(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("height_cm", sa.Numeric(5, 1), nullable=True),
        sa.Column("baseline_weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("goal", sa.String(), nullable=True),
        sa.Column("training_level", sa.String(), nullable=True),
        sa.Column("training_frequency", sa.SmallInteger(), nullable=True),
        sa.Column(
            "allergies",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("bmr_kcal", sa.SmallInteger(), nullable=True),
        sa.Column(
            "onboarding_completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "plan_rebuild_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "sex IS NULL OR sex IN ('male','female')",
            name="ck_user_profiles_sex",
        ),
        sa.CheckConstraint(
            "goal IS NULL OR goal IN ('weight_loss','muscle_gain','maintenance')",
            name="ck_user_profiles_goal",
        ),
        sa.CheckConstraint(
            "training_level IS NULL OR "
            "training_level IN ('beginner','intermediate','advanced')",
            name="ck_user_profiles_training_level",
        ),
        sa.CheckConstraint(
            "training_frequency IS NULL OR training_frequency BETWEEN 2 AND 6",
            name="ck_user_profiles_training_frequency",
        ),
        sa.CheckConstraint(
            "height_cm IS NULL OR height_cm BETWEEN 100 AND 250",
            name="ck_user_profiles_height",
        ),
        sa.CheckConstraint(
            "baseline_weight_kg IS NULL OR baseline_weight_kg BETWEEN 30 AND 300",
            name="ck_user_profiles_weight",
        ),
    )
    op.create_index(
        "ix_user_profiles_onboarding",
        "user_profiles",
        ["onboarding_completed_at"],
    )

    # Триггер на updated_at: при изменении любой строки автоматически бьём now().
    op.execute(
        """
        CREATE OR REPLACE FUNCTION user_profiles_set_updated_at()
        RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_user_profiles_updated_at
        BEFORE UPDATE ON user_profiles
        FOR EACH ROW EXECUTE FUNCTION user_profiles_set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_user_profiles_updated_at ON user_profiles")
    op.execute("DROP FUNCTION IF EXISTS user_profiles_set_updated_at()")
    op.drop_index("ix_user_profiles_onboarding", table_name="user_profiles")
    op.drop_table("user_profiles")
