"""Тесты rule-based композера плана — spec 006 REQ-01..10, NFR-02.

Чистые юниты: composer работает без БД, на in-memory `ExercisePool`.
Проверяем основные сценарии спецификации:
- 4 недели генерируются и содержат strength + cardio;
- equipment_subset соблюдается (REQ-06);
- прогрессия растёт неделя-к-неделе (REQ-09);
- кардио согласовано с целью (REQ-10);
- детерминизм: один и тот же вход → тот же план (NFR-02).
"""

from __future__ import annotations

import pytest

from app.domain.workout_generator import (
    ExercisePool,
    PlannedExercise,
    UserContext,
    compose_plan,
)


# ---------------------------------------------------------------------------
# Test fixtures: «богатый» пул, чтобы заполнялись все слоты
# ---------------------------------------------------------------------------


def _rich_pool() -> list[ExercisePool]:
    """Пул, покрывающий все группы из всех сплитов 2..6 (см. templates.py).

    Имена выбраны так, чтобы compound-эвристика срабатывала там, где
    задумано (squat/bench/row/deadlift).
    """
    return [
        # quads
        ExercisePool(
            id="quads-1",
            name="Barbell Back Squat",
            name_ru="Приседания со штангой",
            primary_muscle_group="quads",
            secondary_muscle_groups=("glutes",),
            equipment=("barbell",),
            body_region="lower",
        ),
        ExercisePool(
            id="quads-2",
            name="Front Squat",
            name_ru="Фронтальные приседания",
            primary_muscle_group="quads",
            secondary_muscle_groups=("core",),
            equipment=("barbell",),
            body_region="lower",
        ),
        # hamstrings
        ExercisePool(
            id="hams-1",
            name="Romanian Deadlift",
            name_ru="Румынская тяга",
            primary_muscle_group="hamstrings",
            secondary_muscle_groups=("glutes",),
            equipment=("barbell",),
            body_region="lower",
        ),
        ExercisePool(
            id="hams-2",
            name="Leg Curl",
            name_ru="Сгибание ног",
            primary_muscle_group="hamstrings",
            secondary_muscle_groups=(),
            equipment=("machine",),
            body_region="lower",
        ),
        # glutes
        ExercisePool(
            id="glut-1",
            name="Hip Thrust",
            name_ru="Ягодичный мост",
            primary_muscle_group="glutes",
            secondary_muscle_groups=("hamstrings",),
            equipment=("barbell", "bench"),
            body_region="lower",
        ),
        # back
        ExercisePool(
            id="back-1",
            name="Barbell Row",
            name_ru="Тяга штанги",
            primary_muscle_group="back",
            secondary_muscle_groups=("biceps",),
            equipment=("barbell",),
            body_region="upper",
        ),
        ExercisePool(
            id="back-2",
            name="Pendlay Row",
            name_ru="Тяга Пендлая",
            primary_muscle_group="back",
            secondary_muscle_groups=("biceps",),
            equipment=("barbell",),
            body_region="upper",
        ),
        # lats
        ExercisePool(
            id="lats-1",
            name="Pullup",
            name_ru="Подтягивания",
            primary_muscle_group="lats",
            secondary_muscle_groups=("biceps",),
            equipment=("pullup_bar",),
            body_region="upper",
        ),
        # chest
        ExercisePool(
            id="chest-1",
            name="Barbell Bench Press",
            name_ru="Жим лёжа",
            primary_muscle_group="chest",
            secondary_muscle_groups=("triceps",),
            equipment=("barbell", "bench"),
            body_region="upper",
        ),
        ExercisePool(
            id="chest-2",
            name="Incline Dumbbell Press",
            name_ru="Жим гантелей на наклонной",
            primary_muscle_group="chest",
            secondary_muscle_groups=("shoulders",),
            equipment=("dumbbell", "bench"),
            body_region="upper",
        ),
        # shoulders
        ExercisePool(
            id="sho-1",
            name="Overhead Press",
            name_ru="Армейский жим",
            primary_muscle_group="shoulders",
            secondary_muscle_groups=("triceps",),
            equipment=("barbell",),
            body_region="upper",
        ),
        # triceps
        ExercisePool(
            id="tri-1",
            name="Tricep Extension",
            name_ru="Разгибания трицепса",
            primary_muscle_group="triceps",
            secondary_muscle_groups=(),
            equipment=("dumbbell",),
            body_region="upper",
        ),
        # biceps
        ExercisePool(
            id="bi-1",
            name="Bicep Curl",
            name_ru="Сгибания бицепса",
            primary_muscle_group="biceps",
            secondary_muscle_groups=(),
            equipment=("dumbbell",),
            body_region="upper",
        ),
        # abs
        ExercisePool(
            id="abs-1",
            name="Plank",
            name_ru="Планка",
            primary_muscle_group="abs",
            secondary_muscle_groups=(),
            equipment=("bodyweight",),
            body_region="core",
        ),
    ]


# ---------------------------------------------------------------------------
# REQ-01: 4 недели × N тренировочных дней
# ---------------------------------------------------------------------------


def test_plan_has_four_weeks() -> None:
    user = UserContext(
        goal="muscle_gain",
        level="intermediate",
        frequency=4,
        equipment_available=("barbell", "bench", "dumbbell", "pullup_bar", "machine"),
        bodyweight_kg=80.0,
    )
    plan = compose_plan(user=user, pool=_rich_pool())
    assert len(plan.weeks) == 4
    assert [w.week_no for w in plan.weeks] == [1, 2, 3, 4]


def test_frequency_drives_strength_days_count() -> None:
    user = UserContext(
        goal="muscle_gain",
        level="intermediate",
        frequency=3,
        equipment_available=("barbell", "bench", "dumbbell", "pullup_bar", "machine"),
    )
    plan = compose_plan(user=user, pool=_rich_pool())
    strength_days = [d for d in plan.weeks[0].days if d.type == "strength"]
    assert len(strength_days) == 3


# ---------------------------------------------------------------------------
# REQ-06: equipment ⊆ equipment_available — без warnings о подборе
# ---------------------------------------------------------------------------


def test_equipment_subset_respected() -> None:
    """Все exercise_id в плане должны быть из пула с допустимым оборудованием."""
    user = UserContext(
        goal="muscle_gain",
        level="beginner",
        frequency=3,
        # Только bodyweight + турник — это «домашний» сценарий.
        equipment_available=("bodyweight", "pullup_bar"),
    )
    pool = _rich_pool()
    plan = compose_plan(user=user, pool=pool)
    pool_by_id = {ex.id: ex for ex in pool}
    available = {"bodyweight", "pullup_bar"}
    for week in plan.weeks:
        for day in week.days:
            if day.type != "strength":
                continue
            for ex in day.exercises:
                if not ex.exercise_id:
                    continue
                src = pool_by_id[ex.exercise_id]
                # Каждое требование инвентаря должно быть в available.
                assert set(src.equipment) <= available | {"bodyweight"}, (
                    f"Упражнение {src.name} требует {src.equipment}, "
                    f"что не подмножество {available}"
                )


def test_limited_equipment_yields_warnings() -> None:
    """Если на группу нечего выбрать — composer добавляет warning, но не падает."""
    user = UserContext(
        goal="muscle_gain",
        level="intermediate",
        frequency=4,
        # Только bodyweight: квадрицепс/спина/грудь нечем нагружать.
        equipment_available=("bodyweight",),
    )
    plan = compose_plan(user=user, pool=_rich_pool())
    assert plan.warnings, "ожидаем хотя бы одно warning о пустых слотах"


# ---------------------------------------------------------------------------
# REQ-09: прогрессия растёт от недели 1 к 4
# ---------------------------------------------------------------------------


def test_progression_grows_for_beginner() -> None:
    user = UserContext(
        goal="muscle_gain",
        level="beginner",
        frequency=2,
        equipment_available=("barbell", "bench", "dumbbell", "pullup_bar", "machine"),
        bodyweight_kg=80.0,
    )
    plan = compose_plan(user=user, pool=_rich_pool())
    # Берём первое упражнение первого strength-дня и сравниваем вес неделя 1 vs 4.
    squat_in_w1 = _find_exercise(plan, week_no=1, exercise_id="quads-1")
    squat_in_w4 = _find_exercise(plan, week_no=4, exercise_id="quads-1")
    assert squat_in_w1 is not None and squat_in_w4 is not None
    assert squat_in_w1.target_weight_kg is not None
    assert squat_in_w4.target_weight_kg is not None
    # Beginner Linear: +step*3 = +7.5 кг для compound.
    assert squat_in_w4.target_weight_kg > squat_in_w1.target_weight_kg


def test_progression_grows_for_intermediate_double() -> None:
    user = UserContext(
        goal="muscle_gain",
        level="intermediate",
        frequency=2,
        equipment_available=("barbell", "bench", "dumbbell", "pullup_bar", "machine"),
        bodyweight_kg=80.0,
    )
    plan = compose_plan(user=user, pool=_rich_pool())
    bench_w1 = _find_exercise(plan, week_no=1, exercise_id="chest-1")
    bench_w4 = _find_exercise(plan, week_no=4, exercise_id="chest-1")
    assert bench_w1 is not None and bench_w4 is not None
    # На W4 либо больше вес, либо больше reps (Double Progression).
    grew_weight = (bench_w4.target_weight_kg or 0) > (
        bench_w1.target_weight_kg or 0
    )
    grew_reps = bench_w4.target_reps_max > bench_w1.target_reps_max
    assert grew_weight or grew_reps


# ---------------------------------------------------------------------------
# REQ-10: кардио согласовано с целью
# ---------------------------------------------------------------------------


def test_weight_loss_has_more_cardio_than_muscle_gain() -> None:
    pool = _rich_pool()
    equip = ("barbell", "bench", "dumbbell", "pullup_bar", "machine")
    user_loss = UserContext(
        goal="weight_loss", level="intermediate", frequency=3, equipment_available=equip
    )
    user_gain = UserContext(
        goal="muscle_gain", level="intermediate", frequency=3, equipment_available=equip
    )
    plan_loss = compose_plan(user=user_loss, pool=pool)
    plan_gain = compose_plan(user=user_gain, pool=pool)
    cardio_loss = [d for d in plan_loss.weeks[0].days if d.type == "cardio"]
    cardio_gain = [d for d in plan_gain.weeks[0].days if d.type == "cardio"]
    assert len(cardio_loss) >= len(cardio_gain)
    assert len(cardio_loss) >= 2  # spec 010 §3 Sc.4 REQ-10: 2-3 сессии
    assert len(cardio_gain) <= 1


# ---------------------------------------------------------------------------
# NFR-02: воспроизводимость — один и тот же вход → один и тот же план
# ---------------------------------------------------------------------------


def test_deterministic_output() -> None:
    user = UserContext(
        goal="muscle_gain",
        level="intermediate",
        frequency=4,
        equipment_available=("barbell", "bench", "dumbbell", "pullup_bar", "machine"),
        bodyweight_kg=78.0,
    )
    pool = _rich_pool()
    a = compose_plan(user=user, pool=pool)
    b = compose_plan(user=user, pool=pool)
    assert a == b


# ---------------------------------------------------------------------------
# REQ-07: 4-8 упражнений на тренировку (фактически — наш потолок зависит
# от шаблона; проверим, что в дне их хотя бы 3 и не более 8)
# ---------------------------------------------------------------------------


def test_exercises_per_day_in_range() -> None:
    user = UserContext(
        goal="muscle_gain",
        level="intermediate",
        frequency=4,
        equipment_available=("barbell", "bench", "dumbbell", "pullup_bar", "machine"),
    )
    plan = compose_plan(user=user, pool=_rich_pool())
    for week in plan.weeks:
        for day in week.days:
            if day.type != "strength":
                continue
            assert 3 <= len(day.exercises) <= 8, (
                f"day {day.name} has {len(day.exercises)} exercises"
            )


# ---------------------------------------------------------------------------
# Защита от невалидной частоты
# ---------------------------------------------------------------------------


def test_invalid_frequency_raises() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        compose_plan(
            user=UserContext(
                goal="muscle_gain",
                level="beginner",
                frequency=7,
                equipment_available=("barbell",),
            ),
            pool=_rich_pool(),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_exercise(
    plan: object, *, week_no: int, exercise_id: str
) -> PlannedExercise | None:
    weeks = getattr(plan, "weeks")
    for w in weeks:
        if w.week_no != week_no:
            continue
        for d in w.days:
            for ex in d.exercises:
                if ex.exercise_id == exercise_id:
                    return ex  # type: ignore[no-any-return]
    return None
