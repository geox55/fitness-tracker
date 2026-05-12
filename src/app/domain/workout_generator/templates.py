"""Шаблоны сплитов, схем подходов и кардио — rule-based ядро spec 006.

Здесь только pure data + чистые функции, никаких ORM/IO. Это REQ-16
fallback: даже если ML-рекоммендер недоступен, композер возвращает
валидный план из этих шаблонов.

Принципы:
- Сплит зависит от `training_frequency` (REQ-05) и `training_level` (REQ-04).
- На каждый день — список «слотов» (целевые primary_muscle_groups + кол-во).
- Параметры подходов (sets × reps) — от цели + уровня (REQ-08), плюс
  REQ-10 кардио согласовано с целью.
- Восстановление: один и тот же primary не повторяется два дня подряд
  (REQ-07 «не нагружать одну группу два дня подряд»).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Goal = Literal["weight_loss", "muscle_gain", "maintenance"]
Level = Literal["beginner", "intermediate", "advanced"]
DayType = Literal["strength", "cardio", "rest"]

# Канонические primary_muscle_group из каталога (см. ml/etl/.../labelling.py).
# Используем как enum-like — composer.py фильтрует упражнения каталога по
# точному совпадению primary_muscle_group.
MuscleGroup = str


@dataclass(frozen=True)
class DaySlot:
    """Один «слот» дня плана: какую группу качаем + сколько упражнений.

    `primary` — target group для слота; secondary не задаём, ранкер сам
    подберёт изоляции/вспомогательные.
    `count` — сколько упражнений нужно подобрать на эту группу.
    """

    primary: MuscleGroup
    count: int


@dataclass(frozen=True)
class DayTemplate:
    """Скелет тренировочного дня. `cardio_minutes` ≠ None для cardio-дней."""

    name: str
    type: DayType
    slots: tuple[DaySlot, ...] = ()
    cardio_minutes: int | None = None


# Сплиты по частоте. day_no — логический день недели 1..7 (см. spec 006 §7).
# Шаги между группами одного функционала ≥1 день (REQ-07).

# 2/неделю: два full-body дня (Mon, Thu).
_SPLIT_2: tuple[tuple[int, DayTemplate], ...] = (
    (
        1,
        DayTemplate(
            name="Full Body A",
            type="strength",
            slots=(
                DaySlot("quads", 1),
                DaySlot("chest", 1),
                DaySlot("back", 1),
                DaySlot("hamstrings", 1),
                DaySlot("abs", 1),
            ),
        ),
    ),
    (
        4,
        DayTemplate(
            name="Full Body B",
            type="strength",
            slots=(
                DaySlot("glutes", 1),
                DaySlot("back", 1),
                DaySlot("chest", 1),
                DaySlot("shoulders", 1),
                DaySlot("abs", 1),
            ),
        ),
    ),
)

# 3/неделю: Push / Pull / Legs (классика).
_SPLIT_3: tuple[tuple[int, DayTemplate], ...] = (
    (
        1,
        DayTemplate(
            name="Push (грудь/плечи/трицепс)",
            type="strength",
            slots=(
                DaySlot("chest", 2),
                DaySlot("shoulders", 1),
                DaySlot("triceps", 1),
                DaySlot("abs", 1),
            ),
        ),
    ),
    (
        3,
        DayTemplate(
            name="Pull (спина/бицепс)",
            type="strength",
            slots=(
                DaySlot("back", 2),
                DaySlot("lats", 1),
                DaySlot("biceps", 1),
            ),
        ),
    ),
    (
        5,
        DayTemplate(
            name="Legs (ноги)",
            type="strength",
            slots=(
                DaySlot("quads", 2),
                DaySlot("hamstrings", 1),
                DaySlot("glutes", 1),
                DaySlot("abs", 1),
            ),
        ),
    ),
)

# 4/неделю: Upper / Lower / Upper / Lower.
_SPLIT_4: tuple[tuple[int, DayTemplate], ...] = (
    (
        1,
        DayTemplate(
            name="Upper A (грудь-приоритет)",
            type="strength",
            slots=(
                DaySlot("chest", 2),
                DaySlot("back", 1),
                DaySlot("shoulders", 1),
                DaySlot("triceps", 1),
            ),
        ),
    ),
    (
        2,
        DayTemplate(
            name="Lower A (квадрицепс-приоритет)",
            type="strength",
            slots=(
                DaySlot("quads", 2),
                DaySlot("glutes", 1),
                DaySlot("hamstrings", 1),
                DaySlot("abs", 1),
            ),
        ),
    ),
    (
        4,
        DayTemplate(
            name="Upper B (спина-приоритет)",
            type="strength",
            slots=(
                DaySlot("back", 2),
                DaySlot("lats", 1),
                DaySlot("chest", 1),
                DaySlot("biceps", 1),
            ),
        ),
    ),
    (
        5,
        DayTemplate(
            name="Lower B (hamstring-приоритет)",
            type="strength",
            slots=(
                DaySlot("hamstrings", 2),
                DaySlot("glutes", 1),
                DaySlot("quads", 1),
                DaySlot("abs", 1),
            ),
        ),
    ),
)

# 5/неделю: Push / Pull / Legs / Upper / Lower.
_SPLIT_5: tuple[tuple[int, DayTemplate], ...] = (
    (1, _SPLIT_3[0][1]),  # Push
    (2, _SPLIT_3[1][1]),  # Pull
    (3, _SPLIT_3[2][1]),  # Legs
    (5, _SPLIT_4[0][1]),  # Upper A
    (6, _SPLIT_4[1][1]),  # Lower A
)

# 6/неделю: PPL × 2.
_SPLIT_6: tuple[tuple[int, DayTemplate], ...] = (
    (1, _SPLIT_3[0][1]),
    (2, _SPLIT_3[1][1]),
    (3, _SPLIT_3[2][1]),
    (5, _SPLIT_3[0][1]),
    (6, _SPLIT_3[1][1]),
    (7, _SPLIT_3[2][1]),
)


_SPLITS: dict[int, tuple[tuple[int, DayTemplate], ...]] = {
    2: _SPLIT_2,
    3: _SPLIT_3,
    4: _SPLIT_4,
    5: _SPLIT_5,
    6: _SPLIT_6,
}


def strength_split(frequency: int) -> tuple[tuple[int, DayTemplate], ...]:
    """Вернуть скелет недели для заданной частоты (REQ-05).

    Бросает ValueError для частот <2 или >6. Профиль валидирует 2..6
    уровнем выше, но защищаемся всё равно.
    """
    if frequency not in _SPLITS:
        raise ValueError(
            f"unsupported training_frequency: {frequency}; allowed: 2..6"
        )
    return _SPLITS[frequency]


# ---------------------------------------------------------------------------
# Кардио — REQ-10
# ---------------------------------------------------------------------------


def cardio_days_for_goal(goal: Goal) -> tuple[tuple[int, DayTemplate], ...]:
    """Сколько кардио-сессий в неделю и в какие дни (REQ-10).

    Заталкиваем кардио в свободные дни сплита; перекрытие со strength —
    забота композера (он сам решит, в какой день встал кардио). Здесь же
    просто список (day_no, template).
    """
    if goal == "weight_loss":
        # 2 сессии — Wed (между Mon/Thu) и Sat. Длительности — нижняя
        # граница, прогрессия в композере добавит +5 мин/неделю.
        return (
            (3, DayTemplate(name="Кардио LISS", type="cardio", cardio_minutes=30)),
            (6, DayTemplate(name="Кардио HIIT", type="cardio", cardio_minutes=25)),
        )
    if goal == "maintenance":
        return (
            (3, DayTemplate(name="Кардио LISS", type="cardio", cardio_minutes=30)),
        )
    # muscle_gain — минимум 1 LISS, ≤30 мин.
    return (
        (3, DayTemplate(name="Кардио LISS", type="cardio", cardio_minutes=20)),
    )


# ---------------------------------------------------------------------------
# Параметры подходов на week=1 (база) — спецификация REQ-08
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SetScheme:
    """Базовая схема подходов на неделе 1. progression.py додумает 2..4."""

    sets: int
    reps_min: int
    reps_max: int
    rpe: int
    rest_seconds: int


def base_scheme(
    *,
    goal: Goal,
    level: Level,
    is_compound: bool,
) -> SetScheme:
    """Подобрать sets×reps×RPE×отдых по цели + уровню + типу упражнения.

    Источник — общепринятые схемы (NSCA, Renaissance Periodization):
    - weight_loss → больше reps (12-15), меньше отдых;
    - muscle_gain → 6-12 reps, средний отдых;
    - maintenance → средняя по обоим;
    - compound получает чуть больший отдых и меньший reps-диапазон,
      чем изоляция.
    """
    if goal == "weight_loss":
        if is_compound:
            return SetScheme(
                sets=3 if level == "beginner" else 4,
                reps_min=10,
                reps_max=12,
                rpe=7,
                rest_seconds=90,
            )
        return SetScheme(
            sets=3,
            reps_min=12,
            reps_max=15,
            rpe=7,
            rest_seconds=60,
        )

    if goal == "muscle_gain":
        if is_compound:
            return SetScheme(
                sets=4 if level != "beginner" else 3,
                reps_min=6 if level == "advanced" else 8,
                reps_max=8 if level == "advanced" else 10,
                rpe=8,
                rest_seconds=150 if level != "beginner" else 120,
            )
        return SetScheme(
            sets=3,
            reps_min=10,
            reps_max=12,
            rpe=8,
            rest_seconds=75,
        )

    # maintenance
    if is_compound:
        return SetScheme(
            sets=3,
            reps_min=8,
            reps_max=10,
            rpe=7,
            rest_seconds=120,
        )
    return SetScheme(
        sets=3,
        reps_min=10,
        reps_max=12,
        rpe=7,
        rest_seconds=75,
    )


# ---------------------------------------------------------------------------
# Эвристика «это compound?»
# ---------------------------------------------------------------------------


_COMPOUND_KEYWORDS: tuple[str, ...] = (
    "squat",
    "deadlift",
    "bench",
    "press",
    "row",
    "pull",
    "chin",
    "dip",
    "clean",
    "snatch",
    "lunge",
    "thrust",
)

_ISOLATION_OVERRIDES: tuple[str, ...] = (
    # Иногда слово «press» встречается в изоляции (calf press, etc.) — даём
    # override-список, который перекрывает compound-эвристику.
    "calf",
    "wrist",
    "curl",
    "fly",
    "kickback",
    "raise",
    "extension",
    "shrug",
)


def is_compound(exercise_name: str, exercise_id: str = "") -> bool:
    """Если в имени/id есть compound-keyword и нет isolation-override — да.

    Это эвристика: каталог не размечен по compound/isolation. На крупной
    выборке (≥500 упражнений по spec 004) она ошибается единицами процентов.
    """
    lower = (exercise_name + " " + exercise_id).lower()
    if any(k in lower for k in _ISOLATION_OVERRIDES):
        return False
    return any(k in lower for k in _COMPOUND_KEYWORDS)
