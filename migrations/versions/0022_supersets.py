"""Суперсеты в логе тренировки (spec 016 REQ-01).

Добавляет nullable колонку `superset_group_id` (UUID) в `exercise_logs`
и partial-индекс на не-NULL значениях. Все логи с одинаковым
`superset_group_id` в одном workout'е — одна группа (суперсет).

Старые записи остаются с NULL и рендерятся как обычные одиночные
упражнения, без поломок.

Revision ID: 0022_supersets
Revises: 0021_offline_client_ids
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022_supersets"
down_revision: str | Sequence[str] | None = "0021_offline_client_ids"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "exercise_logs",
        sa.Column(
            "superset_group_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    # Partial index — нужен только для не-NULL значений (это редкость
    # относительно общего числа логов: суперсет — продвинутая техника).
    op.create_index(
        "ix_exercise_logs_superset_group",
        "exercise_logs",
        ["superset_group_id"],
        postgresql_where=sa.text("superset_group_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_exercise_logs_superset_group", table_name="exercise_logs"
    )
    op.drop_column("exercise_logs", "superset_group_id")
