"""Прогрессия нагрузки по неделям 1..4 — REQ-09 spec 006.

Beginner получает Linear Progression: фиксированный шаг каждую неделю.
Это самая простая и научно подтверждённая схема для новичков (см.
обсуждения Starting Strength / Stronglifts).

Intermediate/advanced — Double Progression: сначала растим повторения
до верхней границы диапазона, потом добавляем вес и сбрасываем reps к
нижней. Это медленнее ломается при stalls.

Все формулы — pure: на вход base_set (sets/reps/weight), уровень и номер
недели; на выход — обновлённый set. Никакой БД, никакой случайности.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Level = Literal["beginner", "intermediate", "advanced"]


@dataclass(frozen=True)
class SetTarget:
    sets: int
    reps_min: int
    reps_max: int
    weight_kg: float | None  # None = «подбирает пользователь по RPE»


# Шаги прогрессии, кг/неделю. Источник — типичные рекомендации программ
# для соответствующих уровней. Beginners быстро прибавляют в первые
# месяцы, advanced — крошечными шагами, micro-loading'ом.
_LP_WEIGHT_STEP_KG: dict[Level, float] = {
    "beginner": 2.5,
    "intermediate": 1.25,
    "advanced": 0.5,
}


def progress_week(
    base: SetTarget,
    *,
    level: Level,
    week_no: int,
    is_compound: bool,
) -> SetTarget:
    """База на week_no=1 → прогрессия на week_no=2..4.

    `is_compound` влияет на величину шага: для компаундов (squat, bench,
    deadlift) шаг крупнее, чем для изоляции (bicep curl). Технически —
    `step *= 1.0 / 0.5` для compound/isolation. Это известная практика
    (BB curl растёт в 2 раза медленнее squat'а).

    Алгоритм:
    - week 1: возвращаем base без изменений (анкер);
    - beginner Linear: +(week_no - 1) * step кг к base.weight_kg;
    - intermediate/advanced Double:
        * на чётной (week_no==2/4) добавляем по 1 повторению к диапазону;
        * на нечётной (week_no==3) — +step kg, reps возвращаем к base.
    """
    if week_no == 1:
        return base
    step = _LP_WEIGHT_STEP_KG[level] * (1.0 if is_compound else 0.5)

    if level == "beginner" or base.weight_kg is None:
        # Без weight_kg прогрессировать в reps — для bodyweight-движений.
        if base.weight_kg is None:
            return SetTarget(
                sets=base.sets,
                reps_min=base.reps_min + (week_no - 1),
                reps_max=base.reps_max + (week_no - 1),
                weight_kg=None,
            )
        return SetTarget(
            sets=base.sets,
            reps_min=base.reps_min,
            reps_max=base.reps_max,
            weight_kg=round(base.weight_kg + step * (week_no - 1), 2),
        )

    # Double Progression. На неделе 2: +1 повторение; неделе 3: +step kg,
    # reps назад; неделе 4: снова +1 повторение от базового, но уже на
    # увеличенном весе (см. ветку для week 3 ниже).
    if week_no == 2:
        return SetTarget(
            sets=base.sets,
            reps_min=base.reps_min + 1,
            reps_max=base.reps_max + 1,
            weight_kg=base.weight_kg,
        )
    if week_no == 4:
        return SetTarget(
            sets=base.sets,
            reps_min=base.reps_min + 1,
            reps_max=base.reps_max + 1,
            weight_kg=round(base.weight_kg + step, 2),
        )
    # week_no == 3
    return SetTarget(
        sets=base.sets,
        reps_min=base.reps_min,
        reps_max=base.reps_max,
        weight_kg=round((base.weight_kg or 0) + step, 2),
    )
