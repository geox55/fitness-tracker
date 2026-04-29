"""Сидинг базовых упражнений (12 штук)."""

from collections.abc import Sequence

from alembic import op

revision: str = "0004_seed_exercises"
down_revision: str | None = "0003_workouts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _array_literal(items: list[str]) -> str:
    """PostgreSQL text[] literal: '{a,b,c}'. Экранируем '."""
    parts = [item.replace("'", "''") for item in items]
    inner = ",".join(parts)
    return f"'{{{inner}}}'::text[]"


_EXERCISES: list[tuple[str, str, str, str, list[str], list[str], int, str]] = [
    # (slug, name_en, name_ru, primary, secondary, equipment, kcal/h, body_region)
    ("barbell_squat", "Barbell Back Squat", "Приседания со штангой", "quads",
     ["glutes", "hamstrings"], ["barbell"], 380, "lower"),
    ("barbell_bench_press", "Barbell Bench Press", "Жим лёжа со штангой", "chest",
     ["triceps", "shoulders"], ["barbell", "bench"], 320, "upper"),
    ("deadlift_conventional", "Deadlift (Conventional)", "Становая тяга", "back",
     ["hamstrings", "glutes", "lats"], ["barbell"], 420, "full_body"),
    ("overhead_press", "Overhead Press", "Жим стоя с гантелями", "shoulders",
     ["triceps"], ["dumbbell"], 280, "upper"),
    ("pullup", "Pull-Ups", "Подтягивания", "lats",
     ["biceps"], ["pullup_bar", "bodyweight"], 360, "upper"),
    ("barbell_row", "Barbell Row", "Тяга штанги в наклоне", "back",
     ["biceps", "lats"], ["barbell"], 310, "upper"),
    ("incline_db_press", "Incline Dumbbell Press", "Жим гантелей на наклонной", "chest",
     ["shoulders", "triceps"], ["dumbbell", "bench"], 290, "upper"),
    ("barbell_lunge", "Barbell Lunge", "Выпады со штангой", "quads",
     ["glutes", "hamstrings"], ["barbell"], 340, "lower"),
    ("bicep_curl", "Bicep Curl", "Подъём на бицепс", "biceps",
     [], ["dumbbell"], 200, "upper"),
    ("tricep_pushdown", "Tricep Pushdown", "Разгибание на трицепс", "triceps",
     [], ["cable"], 200, "upper"),
    ("plank", "Plank", "Планка", "abs",
     ["obliques", "lower_back"], ["bodyweight"], 180, "core"),
    ("running", "Running", "Бег", "cardio",
     [], ["bodyweight", "treadmill"], 600, "full_body"),
]


def upgrade() -> None:
    for slug, name, name_ru, primary, secondary, equipment, kcal, region in _EXERCISES:
        # Все значения — строго из захардкоженного списка выше, SQL-инъекций нет.
        op.execute(
            f"""
            INSERT INTO exercises (
                exercise_id, exercise_name, exercise_name_ru,
                primary_muscle_group, secondary_muscle_group,
                instructions, equipment, calories_burned_per_hour, body_region
            ) VALUES (
                '{slug}',
                '{name.replace("'", "''")}',
                '{name_ru.replace("'", "''")}',
                '{primary}',
                {_array_literal(secondary)},
                '',
                {_array_literal(equipment)},
                {kcal},
                '{region}'
            )
            ON CONFLICT (exercise_id) DO NOTHING
            """
        )


def downgrade() -> None:
    slugs = ", ".join(f"'{e[0]}'" for e in _EXERCISES)
    op.execute(f"DELETE FROM exercises WHERE exercise_id IN ({slugs})")
