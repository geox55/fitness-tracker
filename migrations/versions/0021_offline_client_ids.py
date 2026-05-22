"""Offline-first: client_id для идемпотентности при retry-синхронизации.

spec 015 REQ-01/02. Клиент в офлайне выдаёт каждой мутирующей операции
(POST workout / POST exercise_log / POST inbody) свой UUID и при синке
шлёт его на сервер. Сервер дедуплицирует по этому полю: если запись с
данным `client_id` уже есть — возвращает существующую (200 OK), новой
не создаёт.

Это решает классическую race condition «клиент отправил POST, сервер
принял, ответ потерялся, клиент ретрайт» — без client_id такой ретрайт
создавал бы дубликат.

Колонка nullable — старые записи (до spec 015) и сервер-side операции
(seed, sync с другого канала) останутся без client_id. UNIQUE-индекс
накладывается только на не-NULL значения через partial index.

Revision ID: 0021_offline_client_ids
Revises: 0020_clean_exercise_catalog
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021_offline_client_ids"
down_revision: str | Sequence[str] | None = "0020_clean_exercise_catalog"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for table in ("workouts", "exercise_logs", "inbody_measurements"):
        op.add_column(
            table,
            sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        # Partial UNIQUE — только на не-NULL значениях. Старые записи
        # с NULL не конфликтуют между собой.
        op.create_index(
            f"uq_{table}_client_id",
            table,
            ["client_id"],
            unique=True,
            postgresql_where=sa.text("client_id IS NOT NULL"),
        )


def downgrade() -> None:
    for table in ("inbody_measurements", "exercise_logs", "workouts"):
        op.drop_index(f"uq_{table}_client_id", table_name=table)
        op.drop_column(table, "client_id")
