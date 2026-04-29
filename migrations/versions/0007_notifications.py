"""notification_preferences + notification_outbox — spec 011.

Revision ID: 0007_notifications
Revises: 0006_inbody
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_notifications"
down_revision: str | None = "0006_inbody"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "inbody_reminder",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "plan_update",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "weekly_summary",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "email_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "notification_outbox",
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
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("context_key", sa.Text(), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "type IN ('email_verify','password_reset','inbody_reminder',"
            "'plan_update','weekly_summary')",
            name="ck_notif_type",
        ),
        sa.CheckConstraint(
            "channel IN ('email','in_app')", name="ck_notif_channel"
        ),
        sa.CheckConstraint(
            "status IN ('queued','sent','failed','bounced')",
            name="ck_notif_status",
        ),
        sa.CheckConstraint(
            "channel != 'in_app' OR sent_at IS NOT NULL",
            name="ck_notif_in_app_sent",
        ),
    )
    # Inbox-выборка: непрочитанные пользователя по дате DESC.
    op.create_index(
        "ix_notif_user_unread",
        "notification_outbox",
        ["user_id", "read_at", "created_at"],
    )
    # Debounce-проверка: type+user+channel в окне.
    op.create_index(
        "ix_notif_debounce",
        "notification_outbox",
        ["user_id", "type", "channel", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_notif_debounce", table_name="notification_outbox")
    op.drop_index("ix_notif_user_unread", table_name="notification_outbox")
    op.drop_table("notification_outbox")
    op.drop_table("notification_preferences")
