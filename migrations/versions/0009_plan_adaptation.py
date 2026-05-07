"""plan_rebuild_events — spec 009 (adaptation watcher).

Revision ID: 0009_adaptation
Revises: 0008_forecast
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_adaptation"
down_revision: str | None = "0008_forecast"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "plan_rebuild_events",
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
        sa.Column("trigger", sa.String(), nullable=False),
        sa.Column("target_plan", sa.String(), nullable=False),
        sa.Column(
            "status", sa.String(), nullable=False, server_default="pending"
        ),
        sa.Column("delta_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("delta_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "trigger IN ('weight_change','goal_change','frequency_change',"
            "'cycle_end','manual')",
            name="ck_rebuild_trigger",
        ),
        sa.CheckConstraint(
            "target_plan = 'workout'",
            name="ck_rebuild_target",
        ),
        sa.CheckConstraint(
            "status IN ('pending','auto_applied','user_confirmed','dismissed')",
            name="ck_rebuild_status",
        ),
    )
    op.create_index(
        "ix_rebuild_user_status",
        "plan_rebuild_events",
        ["user_id", "status", "triggered_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_rebuild_user_status", table_name="plan_rebuild_events")
    op.drop_table("plan_rebuild_events")
