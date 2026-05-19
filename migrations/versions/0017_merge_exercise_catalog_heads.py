"""Слияние веток Alembic: избранные/свои упражнения и основная линия.

После spec 014 появились ревизии `0011_user_favorites` → `0012_exercises_owner`,
параллельные линии `0011_pdf_key` → … → `0016_seed_full_catalog`. Без merge
`alembic upgrade head` падает с «multiple heads», из-за чего api-migrate на
деплое завершался с exit 255.

Сама миграция пустая — только фиксирует DAG.

Revision ID: 0017_merge_heads (≤32 символа — ширина `alembic_version.version_num`).
Revises: 0012_exercises_owner, 0016_seed_full_catalog
"""

from collections.abc import Sequence

revision: str = "0017_merge_heads"
down_revision: str | Sequence[str] | None = (
    "0012_exercises_owner",
    "0016_seed_full_catalog",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
