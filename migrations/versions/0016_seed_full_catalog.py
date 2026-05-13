"""Сидинг полного каталога упражнений (873 шт. с переводами).

Раньше каталог заливался отдельным скриптом `make seed`, что приводило
к двум проблемам: (а) на свежем деплое надо было помнить ручной шаг,
(б) на проде каталог проседал до 12 захардкоженных из 0004. Здесь
делаем единый источник истины — JSON `ml/data/processed/exercises_catalog_ru.json`
(собирается ETL'ом, см. `ml/etl/build_exercise_catalog.py` и
`translate_exercises.py`) UPSERT'ится при `alembic upgrade head`.

INSERT ON CONFLICT DO UPDATE — миграция идемпотентна; на повторный
запуск (`alembic upgrade head` без новых ревизий) ничего не делает,
а на новый JSON-снапшот через новую миграцию данные обновятся.

12 строк из 0004_seed_exercises (slug'и вида `barbell_squat`) НЕ
пересекаются по exercise_id с большим каталогом (там slug'и вида
`3_4_sit_up`), поэтому после двух миграций в таблице оказывается
~885 упражнений. Это не баг — 12 из 0004 удобны как стабильные
fixture-id для integration-тестов.

Revision ID: 0016_seed_full_catalog
Revises: 0015_workouts_plan_day_id
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import text

revision: str = "0016_seed_full_catalog"
down_revision: str | None = "0015_workouts_plan_day_id"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Резолв через __file__: migrations/versions/0016... → ../../.. = project root.
# В docker-образе api-migrate ml/ примонтирован read-only по тому же пути
# (`/app/ml/data/processed`), так что вычисление совпадает в любом окружении.
_CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "ml/data/processed/exercises_catalog_ru.json"
)

_UPSERT = text(
    """
    INSERT INTO exercises (
        exercise_id, exercise_name, exercise_name_ru,
        primary_muscle_group, secondary_muscle_group,
        instructions, equipment, calories_burned_per_hour, body_region
    ) VALUES (
        :exercise_id, :exercise_name, :exercise_name_ru,
        :primary_muscle_group, :secondary_muscle_group,
        :instructions, :equipment, :calories_burned_per_hour, :body_region
    )
    ON CONFLICT (exercise_id) DO UPDATE SET
        exercise_name = EXCLUDED.exercise_name,
        exercise_name_ru = COALESCE(
            EXCLUDED.exercise_name_ru, exercises.exercise_name_ru
        ),
        primary_muscle_group = EXCLUDED.primary_muscle_group,
        secondary_muscle_group = EXCLUDED.secondary_muscle_group,
        instructions = CASE
            WHEN length(EXCLUDED.instructions) > length(exercises.instructions)
            THEN EXCLUDED.instructions ELSE exercises.instructions
        END,
        equipment = EXCLUDED.equipment,
        body_region = EXCLUDED.body_region
    """
)


def _load_catalog() -> list[dict[str, object]]:
    if not _CATALOG_PATH.exists():
        raise RuntimeError(
            f"Каталог упражнений не найден: {_CATALOG_PATH}. "
            "В docker проверьте, что ./ml/data/processed смонтирован в "
            "/app/ml/data/processed (см. docker-compose.yml сервисы api / api-migrate)."
        )
    data = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RuntimeError(f"Ожидался JSON-массив в {_CATALOG_PATH}")
    return data


def upgrade() -> None:
    bind = op.get_bind()
    for item in _load_catalog():
        bind.execute(
            _UPSERT,
            {
                "exercise_id": item["exercise_id"],
                "exercise_name": item["exercise_name"],
                "exercise_name_ru": item.get("exercise_name_ru"),
                "primary_muscle_group": item["primary_muscle_group"],
                "secondary_muscle_group": item["secondary_muscle_group"],
                "instructions": item["instructions"],
                "equipment": item["equipment"],
                "calories_burned_per_hour": item.get("calories_burned_per_hour"),
                "body_region": item["body_region"],
            },
        )


def downgrade() -> None:
    # Удаляем ровно те exercise_id, которые залила эта миграция. Если JSON
    # потерян (downgrade в окружении без ml/) — оставляем строки в покое,
    # это безопаснее, чем `DELETE FROM exercises` (снесло бы ещё и 0004).
    if not _CATALOG_PATH.exists():
        return
    ids = [item["exercise_id"] for item in _load_catalog()]
    bind = op.get_bind()
    bind.execute(
        text("DELETE FROM exercises WHERE exercise_id = ANY(:ids)"),
        {"ids": ids},
    )
