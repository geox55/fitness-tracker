"""pdf_export_jobs — spec 010 §3 Scenario 5 / REQ-10..12.

Async-flow для генерации PDF-отчёта: POST создаёт строку pending, фон
готовит PDF и кладёт в storage, GET по job_id отдаёт status + signed URL.
TTL signed URL = 1 час задаётся в сервисе, не на уровне БД.

Revision ID: 0013_pdf_export
Revises: 0012_profile_targets
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013_pdf_export"
down_revision: str | None = "0012_profile_targets"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pdf_export_jobs",
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
            "sections",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("ARRAY[]::text[]"),
        ),
        sa.Column("period_from", sa.Date(), nullable=True),
        sa.Column("period_to", sa.Date(), nullable=True),
        sa.Column("pdf_key", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending','running','ready','failed')",
            name="ck_pdf_export_status",
        ),
    )
    op.create_index(
        "ix_pdf_export_user_created",
        "pdf_export_jobs",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_pdf_export_user_created", table_name="pdf_export_jobs")
    op.drop_table("pdf_export_jobs")
