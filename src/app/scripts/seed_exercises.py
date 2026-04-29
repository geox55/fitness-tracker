"""Загрузка каталога упражнений в БД из JSON, подготовленного ETL.

Идемпотентен: на повторный запуск INSERT ON CONFLICT DO UPDATE.

Запуск:
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
    p.add_argument("json_path", help="Путь к exercises_catalog.json от ETL")
    args = p.parse_args(argv)

    path = Path(args.json_path)
    items = json.loads(path.read_text(encoding="utf-8"))
    print(f"-> seeding {len(items)} exercises", file=sys.stderr)
    inserted = asyncio.run(_run(items))
    print(f"-> upserted {inserted} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
