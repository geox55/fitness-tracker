"""chat_messages + plan_rebuild_events — spec 009.

Revision ID: 0009_chat_adaptation
Revises: 0008_forecast
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_chat_adaptation"
down_revision: str | None = "0008_forecast"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
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
        sa.Column("author", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column(
            "context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("author IN ('user','assistant')", name="ck_chat_author"),
        sa.CheckConstraint(
            "source IN ('scripted','templated','llm','user')",
            name="ck_chat_source",
        ),
        sa.CheckConstraint(
            "char_length(content) <= 4000", name="ck_chat_content_len"
        ),
    )
    op.create_index(
        "ix_chat_user_created", "chat_messages", ["user_id", "created_at"]
    )

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
            "target_plan IN ('workout','nutrition','both')",
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
    op.drop_index("ix_chat_user_created", table_name="chat_messages")
    op.drop_table("chat_messages")
