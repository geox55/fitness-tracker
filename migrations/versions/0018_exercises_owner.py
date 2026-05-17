"""exercises.owner_id — пользовательские упражнения. Spec 014.

Revision ID: 0012_exercises_owner
Revises: 0011_user_favorites

`owner_id IS NULL` — глобальный каталог (сидинг). `owner_id NOT NULL` —
пользовательское: видно только владельцу, может редактироваться и удаляться
им же. CASCADE при удалении пользователя.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012_exercises_owner"
down_revision: str | None = "0011_user_favorites"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "exercises",
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_exercises_owner",
        source_table="exercises",
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    # Partial index: ускоряет GET /exercises/mine и фильтр по owner_id;
    # для глобальных строк (owner_id IS NULL) индекс пустой и места не ест.
    op.create_index(
        "ix_exercises_owner_id",
        "exercises",
        ["owner_id"],
        postgresql_where=sa.text("owner_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_exercises_owner_id", table_name="exercises")
    op.drop_constraint("fk_exercises_owner", "exercises", type_="foreignkey")
    op.drop_column("exercises", "owner_id")
