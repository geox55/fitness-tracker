"""Загрузка каталога упражнений в БД из JSON, подготовленного ETL.

Идемпотентен: на повторный запуск INSERT ON CONFLICT DO UPDATE
(включая обновление exercise_name_ru — если переводы выросли, новые
значения подтянутся).

Запуск:
    # все 873 упражнения с переводами (дефолт)
    uv run python -m app.scripts.seed_exercises

    # явный путь — например, en-only каталог
    uv run python -m app.scripts.seed_exercises ml/data/processed/exercises_catalog.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..db import get_engine

# По умолчанию грузим суперсет — exercise_name_ru заполнен, English-имя
# тоже есть; en-only каталог `exercises_catalog.json` оставляем как
# опцию для тестов без локализации.
_DEFAULT_CATALOG = (
    Path(__file__).resolve().parents[3]
    / "ml/data/processed/exercises_catalog_ru.json"
)

# В docker-образе исходники лежат в /app/src, ml/ монтируется отдельным
# volume в /app/ml. Резолв через parents[3] от /app/src/app/scripts/...
# даёт /app, поэтому путь по умолчанию совпадает с volume mount.

_INSERT = text(
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
        exercise_name_ru = COALESCE(EXCLUDED.exercise_name_ru, exercises.exercise_name_ru),
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


async def _run(items: list[dict[str, object]]) -> int:
    sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with sessionmaker() as session:
        for item in items:
            await session.execute(
                _INSERT,
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
        await session.commit()
    return len(items)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Seed exercises from prepared JSON.")
    p.add_argument(
        "json_path",
        nargs="?",
        default=str(_DEFAULT_CATALOG),
        help=(
            f"Путь к exercises_catalog_*.json от ETL "
            f"(default: {_DEFAULT_CATALOG.relative_to(_DEFAULT_CATALOG.parents[3])})"
        ),
    )
    args = p.parse_args(argv)

    path = Path(args.json_path)
    if not path.exists():
        print(f"!! catalog not found: {path}", file=sys.stderr)
        print(
            "   В docker: проверьте, что ./ml/data/processed смонтирован в /app/ml/data/processed.",
            file=sys.stderr,
        )
        return 2
    items = json.loads(path.read_text(encoding="utf-8"))
    print(f"-> seeding {len(items)} exercises from {path}", file=sys.stderr)
    inserted = asyncio.run(_run(items))
    print(f"-> upserted {inserted} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
