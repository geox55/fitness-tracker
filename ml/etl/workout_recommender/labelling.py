"""Rule-based labelling «user × exercise → релевантно?».

Главный научный модуль ML-блока генератора тренировок (spec 006). Даёт
обучающие метки для рекомендатора, не имея прямой разметки «правильное
упражнение для этого пользователя» (которой в открытых датасетах нет).

Метки формируются как мягкая комбинация:

    relevance(user, exercise) = w_goal·goal_match
                              + w_level·level_match
                              + w_region·region_match
                              + w_balance·balance_match
                              − penalty_equipment

Финальная бинарная label = relevance >= THRESHOLD. Бинаризация нужна для
LightGBM Classifier (binary objective): на квартилях выходит ≈ 30–35%
positives — здоровый class balance, не сильный imbalance.

Решения:

- **w_goal=2.0**: цель — самый сильный сигнал. weight_loss → upper компаунд,
  ноги для калорий, abs/cardio plus; muscle_gain → большие компаунды и
  изоляция всех групп; maintenance → general fitness.

- **w_level=1.0**: beginner отрезает «advanced-only» движения (snatch,
  hang clean, олимпийские). advanced может всё.

- **w_region=0.5**: лёгкий буст для region-баланса. Если у юзера
  «верх + низ + кор» → у каждой региональной группы есть позитивы.

- **penalty_equipment**: если упражнение требует оборудования не из набора
  пользователя — релевантность = 0 жёстко (REQ-06). Это не «soft penalty»,
  а exclusion.

Это **не финальная модель**, а labelling-функция: она обучает модель ловить
non-linear сочетания сигналов (например, advanced + muscle_gain + chest →
benchpress сильнее squat'а). Сами правила — упрощённый proxy «как тренер
бы посоветовал», подбирается так, чтобы LGBM смог найти sub-patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

Goal = Literal["weight_loss", "muscle_gain", "maintenance"]
Level = Literal["beginner", "intermediate", "advanced"]


@dataclass(frozen=True)
class UserContext:
    """Срез user'а в момент labelling. Соответствует Anchor из ETL Dataset-B."""

    goal: Goal
    level: Level
    sex: str
    age: int
    height_cm: float
    weight_kg: float
    body_fat_percent: float
    equipment_available: tuple[str, ...]


@dataclass(frozen=True)
class ExerciseContext:
    """Срез exercise из каталога Dataset-A. equipment в каталоге — list."""

    exercise_id: str
    primary_muscle_group: str
    secondary_muscle_groups: tuple[str, ...]
    equipment: tuple[str, ...]
    body_region: str
    is_advanced: bool


# Пороги бинаризации и веса. Подобраны так, чтобы доля positives попадала
# в 25-40% при «реалистичных» дистрибуциях S3 + полном каталоге.
W_GOAL: Final[float] = 2.0
W_LEVEL: Final[float] = 1.0
W_REGION: Final[float] = 0.5
W_BALANCE: Final[float] = 0.5
RELEVANCE_THRESHOLD: Final[float] = 1.5


# Группы мышц с высоким приоритетом для каждой цели.
# Источник: тренерская эвристика из spec 006 §3 + общий best-practice.
_GOAL_PRIORITY_GROUPS: Final[dict[Goal, frozenset[str]]] = {
    "weight_loss": frozenset(
        # Большие группы → высокий расход; кор для core stability.
        {"quads", "hamstrings", "glutes", "back", "chest", "abs", "lower_back"}
    ),
    "muscle_gain": frozenset(
        {
            "chest",
            "back",
            "lats",
            "quads",
            "hamstrings",
            "glutes",
            "shoulders",
            "biceps",
            "triceps",
        }
    ),
    "maintenance": frozenset(
        {"chest", "back", "quads", "shoulders", "abs", "biceps", "triceps"}
    ),
}

_GOAL_BODY_REGION_BOOST: Final[dict[Goal, frozenset[str]]] = {
    # weight_loss → ноги жгут больше калорий; muscle_gain → весь сплит.
    "weight_loss": frozenset({"lower", "core"}),
    "muscle_gain": frozenset({"upper", "lower"}),
    "maintenance": frozenset({"upper", "lower", "core"}),
}


# Список упражнений-«indicator advanced»: их id (или name-substring) часто
# означают, что движение требует подготовки. Совпадение с этим набором →
# `is_advanced=True` (использует labelling.py при загрузке каталога).
ADVANCED_KEYWORDS: Final[tuple[str, ...]] = (
    "snatch",
    "clean",
    "jerk",
    "muscle_up",
    "muscle-up",
    "pistol",
    "handstand",
    "front_squat",
    "overhead_squat",
    "good_morning",
    "deadlift",  # становая — сильно зависит от техники
)


def is_likely_advanced(exercise_id: str, exercise_name: str) -> bool:
    """Эвристика. Каталог не размечен по сложности — приходится по name'у.

    Учитываем и id (snake_case) и name (Pascal/Free). Для «deadlift»
    помечаем все вариации; уровни intermediate / advanced легко его
    выполняют, beginner получит штраф через level_match.
    """
    lower = (exercise_id + " " + exercise_name).lower()
    return any(k in lower for k in ADVANCED_KEYWORDS)


def _equipment_subset(
    needed: tuple[str, ...], available: tuple[str, ...]
) -> bool:
    """Все элементы `needed` должны быть в `available`. bodyweight — бесплатно.

    Если упражнение требует, например, ['barbell', 'bench'] — оба должны
    быть у пользователя. Это REQ-06: ни одно упражнение не должно
    требовать недоступного оборудования.
    """
    if not needed:
        return True
    avail = set(available) | {"bodyweight"}
    return all(eq in avail for eq in needed)


def _goal_match(user: UserContext, exercise: ExerciseContext) -> float:
    priority = _GOAL_PRIORITY_GROUPS[user.goal]
    if exercise.primary_muscle_group in priority:
        return 1.0
    # Secondary group тоже считаем, но слабее (наполовину).
    if any(g in priority for g in exercise.secondary_muscle_groups):
        return 0.5
    return 0.0


def _level_match(user: UserContext, exercise: ExerciseContext) -> float:
    if user.level == "advanced":
        return 1.0
    if user.level == "intermediate":
        # advanced-движения для intermediate — допустимы, но не приоритет.
        return 0.5 if exercise.is_advanced else 1.0
    # beginner: жёсткое отсечение «advanced» движений.
    return 0.0 if exercise.is_advanced else 1.0


def _region_match(user: UserContext, exercise: ExerciseContext) -> float:
    boost = _GOAL_BODY_REGION_BOOST[user.goal]
    return 1.0 if exercise.body_region in boost else 0.0


def _balance_match(user: UserContext, exercise: ExerciseContext) -> float:
    """Грубый буст для упражнений с secondary группой — это компаунды.

    Компаунды (squat, bench, row) затрагивают несколько групп → лучше
    для time-efficient тренировки, особенно на низких frequency.
    """
    return 1.0 if exercise.secondary_muscle_groups else 0.0


@dataclass(frozen=True)
class RelevanceScore:
    """Результат labelling: и непрерывный score, и финальная binary label."""

    score: float
    label: int  # 0 / 1 — для LGBM binary
    excluded_by_equipment: bool


def relevance(user: UserContext, exercise: ExerciseContext) -> RelevanceScore:
    """Главная функция: посчитать relevance + бинарную метку.

    Equipment-фильтр — жёсткий: при отсутствии нужного экипировки сразу
    отдаём score=0, label=0 + флаг exclusion (нужен для valida логики
    composer'а, чтобы не принять артефакт «модель score=0 случайно»).
    """
    if not _equipment_subset(exercise.equipment, user.equipment_available):
        return RelevanceScore(score=0.0, label=0, excluded_by_equipment=True)

    score = (
        W_GOAL * _goal_match(user, exercise)
        + W_LEVEL * _level_match(user, exercise)
        + W_REGION * _region_match(user, exercise)
        + W_BALANCE * _balance_match(user, exercise)
    )
    return RelevanceScore(
        score=score,
        label=1 if score >= RELEVANCE_THRESHOLD else 0,
        excluded_by_equipment=False,
    )
