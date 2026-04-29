"""inbody_measurements — spec 003.

Revision ID: 0006_inbody
Revises: 0005_user_profile
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_inbody"
down_revision: str | None = "0005_user_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inbody_measurements",
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
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=False),
        sa.Column("height_cm", sa.Numeric(5, 1), nullable=False),
        sa.Column("sex", sa.String(), nullable=False),
        sa.Column("body_fat_percent", sa.Numeric(4, 1), nullable=False),
        sa.Column("muscle_mass_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("body_water_percent", sa.Numeric(4, 1), nullable=True),
        sa.Column("protein_kg", sa.Numeric(4, 2), nullable=True),
        sa.Column("minerals_kg", sa.Numeric(4, 2), nullable=True),
        sa.Column("visceral_fat_level", sa.SmallInteger(), nullable=True),
        sa.Column("bmr_kcal", sa.SmallInteger(), nullable=True),
        sa.Column("fat_free_mass_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("bmi", sa.Numeric(4, 1), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("original_pdf_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("weight_kg BETWEEN 30 AND 300", name="ck_inbody_weight"),
        sa.CheckConstraint("height_cm BETWEEN 100 AND 250", name="ck_inbody_height"),
        sa.CheckConstraint("sex IN ('male','female')", name="ck_inbody_sex"),
        sa.CheckConstraint(
            "body_fat_percent BETWEEN 1 AND 70", name="ck_inbody_body_fat"
        ),
        sa.CheckConstraint(
            "muscle_mass_kg IS NULL OR muscle_mass_kg BETWEEN 5 AND 120",
            name="ck_inbody_muscle_mass",
        ),
        sa.CheckConstraint(
            "body_water_percent IS NULL OR body_water_percent BETWEEN 30 AND 80",
            name="ck_inbody_water",
        ),
        sa.CheckConstraint(
            "protein_kg IS NULL OR protein_kg BETWEEN 1 AND 30",
            name="ck_inbody_protein",
        ),
        sa.CheckConstraint(
            "minerals_kg IS NULL OR minerals_kg BETWEEN 0.5 AND 10",
            name="ck_inbody_minerals",
        ),
        sa.CheckConstraint(
            "visceral_fat_level IS NULL OR visceral_fat_level BETWEEN 1 AND 30",
            name="ck_inbody_visceral",
        ),
        sa.CheckConstraint(
            "bmr_kcal IS NULL OR bmr_kcal BETWEEN 500 AND 5000",
            name="ck_inbody_bmr",
        ),
        sa.CheckConstraint(
            "fat_free_mass_kg IS NULL OR fat_free_mass_kg BETWEEN 20 AND 200",
            name="ck_inbody_ffm",
        ),
        sa.CheckConstraint(
            "source IN ('manual','pdf')", name="ck_inbody_source"
        ),
    )
    op.create_index(
        "ix_inbody_user_measured",
        "inbody_measurements",
        ["user_id", "measured_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_inbody_user_measured", table_name="inbody_measurements")
    op.drop_table("inbody_measurements")
