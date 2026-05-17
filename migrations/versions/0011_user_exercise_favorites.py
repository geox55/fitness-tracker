"""user_exercise_favorites — spec 014.

Revision ID: 0011_user_favorites
Revises: 0010_pdf_jobs

NB: на ветке feat/spec-010-013 номер 0011 уже занят 0011_inbody_pdf_key.
При мердже этих веток одну из миграций нужно перенумеровать; alembic-цепочка
связана через down_revision, поэтому ID-конфликта не будет — только filename.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011_user_favorites"
down_revision: str | None = "0010_pdf_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_exercise_favorites",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exercise_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercises.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "exercise_id", name="pk_user_exercise_favorites"
        ),
    )
    # Индекс для вкладки «Избранные» (sort by created_at DESC по конкретному user_id).
    # PK уже даёт btree (user_id, exercise_id), но он не помогает сортировать по
    # created_at без random I/O.
    op.create_index(
        "ix_user_exercise_favorites_user_created",
        "user_exercise_favorites",
        ["user_id", sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_exercise_favorites_user_created",
        table_name="user_exercise_favorites",
    )
    op.drop_table("user_exercise_favorites")
