"""inbody_measurements: original_pdf_url → original_pdf_key.

Колонка хранит storage-key (s3 path), а не публичный URL: фактический URL
выдаётся signed_url'ом в API на лету (NFR-04 spec 013). Производственных
данных в этой колонке нет (фича PDF-импорта только что выкачена и поле
было только что добавлено), поэтому делаем простой rename без миграции
данных. Если бы данные были — пришлось бы их «обрезать» от public_base.

Revision ID: 0011_pdf_key
Revises: 0010_pdf_jobs
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0011_pdf_key"
down_revision: str | None = "0010_pdf_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "inbody_measurements",
        "original_pdf_url",
        new_column_name="original_pdf_key",
    )


def downgrade() -> None:
    op.alter_column(
        "inbody_measurements",
        "original_pdf_key",
        new_column_name="original_pdf_url",
    )
