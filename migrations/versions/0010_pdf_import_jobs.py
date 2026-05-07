"""pdf_import_jobs — spec 013.

Revision ID: 0010_pdf_jobs
Revises: 0009_adaptation
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_pdf_jobs"
down_revision: str | None = "0009_adaptation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pdf_import_jobs",
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
        sa.Column("template", sa.String(32), nullable=True),
        sa.Column(
            "extracted",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "confidence",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "missing_fields",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("ARRAY[]::text[]"),
        ),
        sa.Column("temp_pdf_key", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('parsing','ready','partial','failed',"
            "'not_inbody','encrypted','scanned_unsupported')",
            name="ck_pdf_job_status",
        ),
    )
    op.create_index(
        "ix_pdf_job_user_created",
        "pdf_import_jobs",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_pdf_job_user_created", table_name="pdf_import_jobs")
    op.drop_table("pdf_import_jobs")
