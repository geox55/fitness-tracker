"""Композер плана — собирает spec 006 §7 структуру из чистых данных.

На вход: пользователь (goal/level/frequency/equipment), пул упражнений
каталога. На выход: 4 недели → дни → упражнения с прогрессией.

Алгоритм:
1. Берём `strength_split(frequency)` — скелет недели.
2. На каждом слоте дня фильтруем каталог по `equipment ⊆ available` и
   `primary_muscle_group == slot.primary`; ранжируем по релевантности
   цели/уровню, берём top-N (slot.count).
3. Каждому упражнению считаем `SetScheme` через `base_scheme`, прогрессию
   неделя-к-неделе через `progress_week`.
4. Добавляем кардио-дни через `cardio_days_for_goal`.
5. Валидируем итог: equipment ⊆ available, нет дублей внутри дня,
   соседние strength-дни не повторяют одну primary_group (REQ-07).

Это REQ-16 fallback: если ML-ранкер недоступен, композер сам выдаёт
валидный план. ML мог бы лучше расставлять упражнения по релевантности —
сейчас мы используем простой scoring (см. `_score_exercise`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .progression import SetTarget, progress_week
from .templates import (
    DayTemplate,
    Goal,
    Level,
    SetScheme,
    base_scheme,
    cardio_days_for_goal,
    is_compound,
    strength_split,
)

# Версия композера — пишем в WorkoutPlan.model_version для трассировки.
COMPOSER_VERSION = "rule-based-0.1.0"


@dataclass(frozen=True)
class ExercisePool:
    """Карточка упражнения для композера. Эквивалент каталога spec 004.

    Поля совпадают с `Exercise` ORM-модели, но без БД-зависимостей —
    тесты композера не должны поднимать Postgres.
    """

    id: str  # UUID как строка
    name: str
    name_ru: str | None
    primary_muscle_group: str
    secondary_muscle_groups: tuple[str, ...]
    equipment: tuple[str, ...]
    body_region: str


@dataclass(frozen=True)
class UserContext:
    """Слепок пользователя для генератора. Только то, что нужно
    композеру; PII не передаём (NFR-04).
    """

    goal: Goal
    level: Level
    frequency: int  # 2..6
    equipment_available: tuple[str, ...]
    # Baseline weight для подбора стартовых рабочих весов — опционально.
    bodyweight_kg: float | None = None


@dataclass(frozen=True)
class PlannedExercise:
    """Одно упражнение в плане — выход композера для одного дня/недели."""

    exercise_id: str
    exercise_name: str
    order_no: int
    target_sets: int
    target_reps_min: int
    target_reps_max: int
    target_rpe: int | None
    rest_seconds: int | None
    target_weight_kg: float | None
    notes: str | None


@dataclass(frozen=True)
class PlannedDay:
    day_no: int
    name: str
    type: Literal["strength", "cardio", "rest"]
    exercises: tuple[PlannedExercise, ...] = ()


@dataclass(frozen=True)
class PlannedWeek:
    week_no: int
    days: tuple[PlannedDay, ...]


@dataclass(frozen=True)
class PlannedPlan:
    """Финальный план — 4 недели × дни × упражнения, плюс warnings."""

    weeks: tuple[PlannedWeek, ...]
    warnings: tuple[str, ...] = ()
    model_version: str = COMPOSER_VERSION


# ---------------------------------------------------------------------------
# Pool filtering & ranking
# ---------------------------------------------------------------------------


def _equipment_ok(
    needed: tuple[str, ...], available: tuple[str, ...]
) -> bool:
    """Все элементы `needed` должны быть в `available`. bodyweight — бесплатно.

    Дублирует логику labelling.py — выделено отдельно, чтобы composer не
    тянул весь ETL-стек.
    """
    if not needed:
        return True
    avail = set(available) | {"bodyweight"}
    return all(eq in avail for eq in needed)


# Какие группы критичны для каждой цели — для бонусов в `_score_exercise`.
_GOAL_PRIORITY_GROUPS: dict[Goal, frozenset[str]] = {
    "weight_loss": frozenset(
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

# Beginner — компаундам бонус (Stronglifts / Starting Strength rationale).
# Advanced — изоляции тоже плюс (есть бюджет на детализацию).
_LEVEL_COMPOUND_BONUS: dict[Level, float] = {
    "beginner": 1.0,
    "intermediate": 0.5,
    "advanced": 0.0,
}


def _score_exercise(
    ex: ExercisePool,
    *,
    user: UserContext,
    target_primary: str,
) -> float:
    """Грубая релевантность для ранжирования внутри слота.

    Не претендует на ML-качество — просто несколько эвристических плюсов:
    - +2.0 за точное совпадение primary с целью слота;
    - +1.0 если primary входит в `_GOAL_PRIORITY_GROUPS[goal]`;
    - +0.5 если secondary пересекает priority groups;
    - +bonus за compound на beginner-уровне.
    """
    score = 0.0
    if ex.primary_muscle_group == target_primary:
        score += 2.0
    priority = _GOAL_PRIORITY_GROUPS[user.goal]
    if ex.primary_muscle_group in priority:
        score += 1.0
    if any(g in priority for g in ex.secondary_muscle_groups):
        score += 0.5
    if is_compound(ex.name, ex.id):
        score += _LEVEL_COMPOUND_BONUS[user.level]
    return score


def _pick_for_slot(
    pool: list[ExercisePool],
    *,
    user: UserContext,
    target_primary: str,
    count: int,
    already_used: set[str],
    ml_scores: dict[str, float] | None = None,
) -> list[ExercisePool]:
    """Вернуть top-`count` упражнений каталога для слота.

    Условия:
    - exercise.primary_muscle_group == target_primary (жёсткий matcher);
    - equipment ⊆ user.equipment_available;
    - exercise.id ∉ already_used (не повторяем в этом же дне).

    Ранжирование:
    - если `ml_scores` передан — используем `ml_scores[ex.id]` (выше = лучше);
    - иначе rule-based `_score_exercise` (REQ-16 fallback).

    Композер при этом сохраняет hard-constraints (primary, equipment,
    no-dupes) — ML только ранжирует кандидатов, отобранных жёсткими
    фильтрами. Это spec 006 §2: гибридная схема, ML не должна вылезать
    за границы equipment'а пользователя.

    Если матчей <count — возвращаем сколько есть. Композер потом отметит
    `warnings` если слот не наполнился (Scenario 2).
    """
    candidates = [
        ex
        for ex in pool
        if ex.primary_muscle_group == target_primary
        and ex.id not in already_used
        and _equipment_ok(ex.equipment, user.equipment_available)
    ]

    def _rank(ex: ExercisePool) -> float:
        if ml_scores is not None and ex.id in ml_scores:
            return ml_scores[ex.id]
        return _score_exercise(ex, user=user, target_primary=target_primary)

    # Стабильная сортировка: сначала по score desc, потом по id для
    # детерминизма (NFR-02 «один и тот же seed/вход → тот же план»).
    candidates.sort(key=lambda ex: (-_rank(ex), ex.id))
    return candidates[:count]


# ---------------------------------------------------------------------------
# Compose
# ---------------------------------------------------------------------------


def _initial_weight(
    ex: ExercisePool,
    *,
    user: UserContext,
    scheme: SetScheme,
) -> float | None:
    """Стартовый рабочий вес на неделю 1.

    Без данных истории подобрать точный вес нельзя — отдаём `None`
    для bodyweight-движений (без оборудования) и небольшую долю
    bodyweight_kg для остальных. Это эвристика для beginner; для
    intermediate/advanced пользователь подкорректирует по RPE.
    """
    if not ex.equipment or "bodyweight" in ex.equipment and len(ex.equipment) == 1:
        return None
    if user.bodyweight_kg is None:
        return None
    # Грубая база: 30% bodyweight для compound, 15% для изоляции на
    # beginner; для intermediate/advanced поднимаем.
    base_pct = 0.30 if is_compound(ex.name, ex.id) else 0.15
    level_mult = {
        "beginner": 1.0,
        "intermediate": 1.4,
        "advanced": 1.8,
    }[user.level]
    weight = user.bodyweight_kg * base_pct * level_mult
    # Округляем к ближайшим 2.5 кг — стандартный шаг блинов.
    return round(weight / 2.5) * 2.5


def _compose_strength_day(
    *,
    day_no: int,
    template: DayTemplate,
    pool: list[ExercisePool],
    user: UserContext,
    week_no: int,
    base_targets: dict[tuple[str, str], SetTarget],
    ml_scores: dict[str, float] | None = None,
) -> tuple[PlannedDay, dict[tuple[str, str], SetTarget], list[str]]:
    """Собрать один strength-день и вернуть его + обновлённую таблицу
    `base_targets` (id → SetTarget на неделе 1, нужна для последующих
    недель), + warnings.

    На week_no=1 заполняем pool, считаем base scheme, кладём в
    `base_targets`. На weeks 2..4 берём из `base_targets[id]` и
    прогрессируем через progress_week.
    """
    warnings: list[str] = []
    exercises: list[PlannedExercise] = []
    used: set[str] = set()
    order_no = 1
    for slot in template.slots:
        if week_no == 1:
            picked = _pick_for_slot(
                pool,
                user=user,
                target_primary=slot.primary,
                count=slot.count,
                already_used=used,
                ml_scores=ml_scores,
            )
            if len(picked) < slot.count:
                warnings.append(
                    f"slot '{slot.primary}': подобрано {len(picked)}/{slot.count} "
                    f"упражнений (день {template.name})"
                )
            for ex in picked:
                used.add(ex.id)
                scheme = base_scheme(
                    goal=user.goal,
                    level=user.level,
                    is_compound=is_compound(ex.name, ex.id),
                )
                weight = _initial_weight(ex, user=user, scheme=scheme)
                target = SetTarget(
                    sets=scheme.sets,
                    reps_min=scheme.reps_min,
                    reps_max=scheme.reps_max,
                    weight_kg=weight,
                )
                # Запомним базу для следующих недель.
                base_targets[(template.name, ex.id)] = target
                exercises.append(
                    PlannedExercise(
                        exercise_id=ex.id,
                        exercise_name=ex.name_ru or ex.name,
                        order_no=order_no,
                        target_sets=target.sets,
                        target_reps_min=target.reps_min,
                        target_reps_max=target.reps_max,
                        target_rpe=scheme.rpe,
                        rest_seconds=scheme.rest_seconds,
                        target_weight_kg=target.weight_kg,
                        notes=None,
                    )
                )
                order_no += 1
        else:
            # Восстанавливаем «scaffold» этого же дня — итерируем по
            # ключам base_targets с этим template.name в стабильном порядке.
            day_keys = [
                k for k in base_targets if k[0] == template.name
            ]
            for tpl_name, ex_id in day_keys:
                base = base_targets[(tpl_name, ex_id)]
                pool_lookup = next(
                    (ex for ex in pool if ex.id == ex_id), None
                )
                if pool_lookup is None:
                    continue  # каталог изменился, скипаем
                progressed = progress_week(
                    base,
                    level=user.level,
                    week_no=week_no,
                    is_compound=is_compound(
                        pool_lookup.name, pool_lookup.id
                    ),
                )
                scheme = base_scheme(
                    goal=user.goal,
                    level=user.level,
                    is_compound=is_compound(
                        pool_lookup.name, pool_lookup.id
                    ),
                )
                exercises.append(
                    PlannedExercise(
                        exercise_id=pool_lookup.id,
                        exercise_name=pool_lookup.name_ru or pool_lookup.name,
                        order_no=order_no,
                        target_sets=progressed.sets,
                        target_reps_min=progressed.reps_min,
                        target_reps_max=progressed.reps_max,
                        target_rpe=scheme.rpe,
                        rest_seconds=scheme.rest_seconds,
                        target_weight_kg=progressed.weight_kg,
                        notes=None,
                    )
                )
                order_no += 1
            # На weeks 2..4 не итерируем по template.slots — просто
            # копируем тот же набор упражнений, что был на week 1.
            break

    return (
        PlannedDay(
            day_no=day_no,
            name=template.name,
            type="strength",
            exercises=tuple(exercises),
        ),
        base_targets,
        warnings,
    )


def _compose_cardio_day(
    *,
    day_no: int,
    template: DayTemplate,
    week_no: int,
    goal: Goal,
) -> PlannedDay:
    """Кардио — отдельный day_no без упражнений каталога.

    Прогрессия: +5 мин/неделю до 45 мин для weight_loss; для остальных
    держим базу. Длительность кладём в `notes` (UI её отрендерит).
    """
    minutes = template.cardio_minutes or 0
    if goal == "weight_loss":
        minutes = min(minutes + 5 * (week_no - 1), 45)
    return PlannedDay(
        day_no=day_no,
        name=template.name,
        type="cardio",
        exercises=(
            PlannedExercise(
                exercise_id="",  # plug — нет каталожного упражнения для LISS/HIIT
                exercise_name=template.name,
                order_no=1,
                target_sets=1,
                target_reps_min=1,
                target_reps_max=1,
                target_rpe=6,
                rest_seconds=None,
                target_weight_kg=None,
                notes=f"{minutes} мин",
            ),
        ),
    )


def compose_plan(
    *,
    user: UserContext,
    pool: list[ExercisePool],
    ml_scores: dict[str, float] | None = None,
    model_version: str | None = None,
) -> PlannedPlan:
    """Собрать 4-недельный план для пользователя.

    Контракт:
    - возвращает 4 недели с одинаковым составом упражнений, разные
      target_weight/reps согласно прогрессии (REQ-09);
    - все exercise_id в плане доступны в pool;
    - все упражнения удовлетворяют `equipment ⊆ user.equipment_available`;
    - warnings — список человеко-читаемых notes для пользователя
      (Scenario 2: «ограниченный набор → советуем добавить N»).

    `ml_scores` — гибридная схема spec 006 §2: если передан, упражнения
    внутри каждого слота ранжируются ML-скором, иначе rule-based
    `_score_exercise` (REQ-16 fallback). Hard-constraints (equipment,
    primary group, no-dupes) композер держит сам — ML не вылезает.

    `model_version` — что записать в `PlannedPlan.model_version`. По
    умолчанию `COMPOSER_VERSION`; при гибриде сервис передаёт строку
    вида `"hybrid-{composer}+{ranker}"` для трассировки.
    """
    split = strength_split(user.frequency)
    cardio_days = cardio_days_for_goal(user.goal)
    all_warnings: list[str] = []

    weeks: list[PlannedWeek] = []
    # Одна и та же карта base_targets на все 4 недели — composer её
    # наполняет на week 1 и читает на week 2..4.
    base_targets: dict[tuple[str, str], SetTarget] = {}

    # Кардио-дни не должны налезать на strength: если конфликт,
    # сдвигаем кардио в первый свободный day_no 1..7.
    strength_days = {day_no for day_no, _ in split}
    resolved_cardio: list[tuple[int, DayTemplate]] = []
    for day_no, tpl in cardio_days:
        used_days = strength_days | {d for d, _ in resolved_cardio}
        target_day = day_no
        while target_day in used_days and target_day <= 7:
            target_day += 1
        if target_day > 7:
            # Все 7 дней забиты strength — кардио не помещается, скипаем.
            all_warnings.append(
                "кардио опущено: все 7 дней заняты strength-сессиями"
            )
            continue
        resolved_cardio.append((target_day, tpl))

    for week_no in range(1, 5):
        days: list[PlannedDay] = []
        for day_no, tpl in split:
            day, base_targets, warnings = _compose_strength_day(
                day_no=day_no,
                template=tpl,
                pool=pool,
                user=user,
                week_no=week_no,
                base_targets=base_targets,
                ml_scores=ml_scores,
            )
            days.append(day)
            if week_no == 1:
                all_warnings.extend(warnings)
        for day_no, tpl in resolved_cardio:
            days.append(
                _compose_cardio_day(
                    day_no=day_no, template=tpl, week_no=week_no, goal=user.goal
                )
            )
        days.sort(key=lambda d: d.day_no)
        weeks.append(PlannedWeek(week_no=week_no, days=tuple(days)))

    # Финальный валидатор: equipment match, нет дублей в дне, нет
    # повторов primary_group в соседних strength-днях.
    validator_warnings = _validate_plan(weeks, pool=pool, user=user)
    all_warnings.extend(validator_warnings)

    return PlannedPlan(
        weeks=tuple(weeks),
        warnings=tuple(_dedup(all_warnings)),
        model_version=model_version or COMPOSER_VERSION,
    )


def _dedup(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def _validate_plan(
    weeks: list[PlannedWeek],
    *,
    pool: list[ExercisePool],
    user: UserContext,
) -> list[str]:
    """REQ-06/07: equipment ⊆ available, нет двух дней одной группы подряд.

    Возвращает список human-readable предупреждений (вместо бросания
    исключений) — план всё равно валиден, но UI покажет «осторожно».
    """
    pool_by_id = {ex.id: ex for ex in pool}
    warnings: list[str] = []
    seen_eq_violations: set[str] = set()
    for week in weeks:
        strength_days = [d for d in week.days if d.type == "strength"]
        # REQ-06: equipment check.
        for day in strength_days:
            for ex in day.exercises:
                if not ex.exercise_id:
                    continue
                pool_ex = pool_by_id.get(ex.exercise_id)
                if pool_ex is None:
                    continue
                if not _equipment_ok(
                    pool_ex.equipment, user.equipment_available
                ):
                    key = f"{ex.exercise_name} требует {pool_ex.equipment}"
                    if key not in seen_eq_violations:
                        warnings.append(
                            f"упражнение «{ex.exercise_name}» требует оборудование "
                            f"{list(pool_ex.equipment)}, которое не указано в профиле"
                        )
                        seen_eq_violations.add(key)
        # REQ-07: одна primary_group не должна повторяться в соседних
        # strength-днях (по day_no). Считаем «соседними» дни с разницей 1.
        strength_days.sort(key=lambda d: d.day_no)
        for i in range(len(strength_days) - 1):
            a, b = strength_days[i], strength_days[i + 1]
            if b.day_no - a.day_no != 1:
                continue
            groups_a = {
                pool_by_id[ex.exercise_id].primary_muscle_group
                for ex in a.exercises
                if ex.exercise_id in pool_by_id
            }
            groups_b = {
                pool_by_id[ex.exercise_id].primary_muscle_group
                for ex in b.exercises
                if ex.exercise_id in pool_by_id
            }
            overlap = groups_a & groups_b
            if overlap:
                warnings.append(
                    f"неделя {week.week_no}: соседние дни {a.day_no}/{b.day_no} "
                    f"повторяют группу {sorted(overlap)}"
                )
    return warnings
