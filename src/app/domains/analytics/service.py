"""Сервис аналитики: агрегаты для главного экрана.

Все вычисления — на стороне БД, чтобы не тащить тысячи логов в Python.
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..catalog.models import Exercise
from ..workouts.models import ExerciseLog, Workout
from .schemas import (
    OverviewMetrics,
    OverviewResponse,
    RecentWorkoutItem,
    StrengthPoint,
    StrengthProgress,
)

STRENGTH_WINDOW_DAYS = 30


def _month_start(d: date) -> date:
    return d.replace(day=1)


def _prev_month_start(d: date) -> date:
    first = _month_start(d)
    if first.month == 1:
        return first.replace(year=first.year - 1, month=12)
    return first.replace(month=first.month - 1)


def _format_day_label(dt: datetime) -> str:
    months_ru = [
        "янв",
        "фев",
        "мар",
        "апр",
        "мая",
        "июн",
        "июл",
        "авг",
        "сен",
        "окт",
        "ноя",
        "дек",
    ]
    return f"{dt.day} {months_ru[dt.month - 1]}"


async def _tonnage_for_period(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    start: datetime,
    end: datetime,
) -> int:
    stmt = (
        select(func.coalesce(func.sum(ExerciseLog.reps * ExerciseLog.weight_kg), 0))
        .join(Workout, Workout.id == ExerciseLog.workout_id)
        .where(
            Workout.user_id == user_id,
            Workout.status.in_(("completed", "auto_finished")),
            Workout.performed_at >= start,
            Workout.performed_at < end,
            ExerciseLog.skipped.is_(False),
        )
    )
    value = (await session.execute(stmt)).scalar_one()
    return int(value)


async def _workouts_count(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    start: datetime,
    end: datetime,
) -> int:
    stmt = select(func.count(Workout.id)).where(
        Workout.user_id == user_id,
        Workout.status.in_(("completed", "auto_finished")),
        Workout.performed_at >= start,
        Workout.performed_at < end,
    )
    return int((await session.execute(stmt)).scalar_one())


async def _active_streak(session: AsyncSession, *, user_id: uuid.UUID) -> int:
    """Количество последовательных дней с тренировкой, оканчивающихся сегодня
    или вчера. Если последняя тренировка >1 дня назад — стрик 0."""
    today = datetime.now(UTC).date()
    stmt = (
        select(func.distinct(func.date(Workout.performed_at)).label("d"))
        .where(
            Workout.user_id == user_id,
            Workout.status.in_(("completed", "auto_finished")),
        )
        .order_by(func.date(Workout.performed_at).desc())
        .limit(60)
    )
    rows = (await session.execute(stmt)).all()
    if not rows:
        return 0
    days = [r.d for r in rows]
    # допускаем "вчера" как стартовую точку (сегодня ещё не было тренировки)
    pivot = today
    if days[0] != today and days[0] != today - timedelta(days=1):
        return 0
    streak = 0
    for d in days:
        if d == pivot or d == pivot - timedelta(days=1):
            streak += 1
            pivot = d - timedelta(days=1)
        else:
            break
    return streak


async def _recent(
    session: AsyncSession, *, user_id: uuid.UUID, limit: int
) -> list[RecentWorkoutItem]:
    """Последние N завершённых тренировок с краткой сводкой."""
    workouts_q = (
        select(Workout)
        .where(
            Workout.user_id == user_id,
            Workout.status.in_(("completed", "auto_finished")),
        )
        .order_by(Workout.performed_at.desc())
        .limit(limit)
    )
    workouts = (await session.execute(workouts_q)).scalars().all()
    items: list[RecentWorkoutItem] = []
    for w in workouts:
        # агрегаты по логам
        logs_q = select(
            func.count(ExerciseLog.id),
            func.coalesce(func.max(ExerciseLog.reps), 0),
            func.coalesce(func.max(ExerciseLog.weight_kg), 0),
        ).where(ExerciseLog.workout_id == w.id, ExerciseLog.skipped.is_(False))
        sets, max_reps, max_weight = (await session.execute(logs_q)).one()
        items.append(
            RecentWorkoutItem(
                id=w.id,
                performed_at=w.performed_at,
                day_label=_format_day_label(w.performed_at),
                title=w.notes or "Тренировка",
                sets=int(sets or 0),
                reps=int(max_reps or 0),
                weight_kg=int(max_weight or 0),
                kind="other",
            )
        )
    return items


async def _pick_top_exercise(
    session: AsyncSession, *, user_id: uuid.UUID, since: datetime
) -> tuple[uuid.UUID, str | None] | None:
    """Самое нагружаемое упражнение пользователя за окно: больше всего сетов.

    При равенстве — упражнение с большим max-весом (детерминированный
    тай-брейкер, чтобы UI не прыгал между двумя одинаковыми кандидатами).
    """
    stmt = (
        select(
            ExerciseLog.exercise_id,
            Exercise.exercise_name_ru,
            Exercise.exercise_name,
            func.count(ExerciseLog.id).label("sets"),
            func.max(ExerciseLog.weight_kg).label("max_weight"),
        )
        .join(Workout, Workout.id == ExerciseLog.workout_id)
        .join(Exercise, Exercise.id == ExerciseLog.exercise_id)
        .where(
            Workout.user_id == user_id,
            Workout.status.in_(("completed", "auto_finished")),
            ExerciseLog.skipped.is_(False),
            ExerciseLog.logged_at >= since,
        )
        .group_by(
            ExerciseLog.exercise_id,
            Exercise.exercise_name_ru,
            Exercise.exercise_name,
        )
        .order_by(
            func.count(ExerciseLog.id).desc(),
            func.max(ExerciseLog.weight_kg).desc(),
        )
        .limit(1)
    )
    row = (await session.execute(stmt)).first()
    if row is None:
        return None
    title = row.exercise_name_ru or row.exercise_name
    return row.exercise_id, title


async def _strength_points(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    exercise_id: uuid.UUID,
    since: datetime,
) -> list[tuple[date, float]]:
    """Max-вес по дням для упражнения, отсортирован по возрастанию даты."""
    log_date = func.date(ExerciseLog.logged_at).label("d")
    stmt = (
        select(log_date, func.max(ExerciseLog.weight_kg).label("max_weight"))
        .join(Workout, Workout.id == ExerciseLog.workout_id)
        .where(
            Workout.user_id == user_id,
            ExerciseLog.exercise_id == exercise_id,
            ExerciseLog.skipped.is_(False),
            ExerciseLog.logged_at >= since,
        )
        .group_by(log_date)
        .order_by(log_date)
    )
    rows = (await session.execute(stmt)).all()
    return [(row.d, float(row.max_weight)) for row in rows]


def _build_strength_progress(
    *,
    title: str | None,
    rows: Sequence[tuple[date, float]],
    window_start: date,
) -> StrengthProgress | None:
    """Чистая часть: превратить агрегаты БД в StrengthProgress.

    Возвращает None (UI скроет блок), если:
    - записей вообще нет;
    - точка всего одна — линию по одной точке рисовать бессмысленно,
      «прогресс» невозможно показать (REQ: график осмыслен от 2 точек).
    day_offset = days from window_start, чтобы клиент рисовал X-ось в
    днях, а не датах.
    """
    if len(rows) < 2:
        return None
    points = [
        StrengthPoint(
            day_offset=(d - window_start).days,
            weight_kg=weight,
        )
        for d, weight in rows
    ]
    current_max = max(weight for _, weight in rows)
    return StrengthProgress(
        exercise_title=title,
        current_max_kg=round(current_max),
        points=points,
    )


async def _strength(
    session: AsyncSession, *, user_id: uuid.UUID, now: datetime
) -> StrengthProgress | None:
    since = now - timedelta(days=STRENGTH_WINDOW_DAYS)
    top = await _pick_top_exercise(session, user_id=user_id, since=since)
    if top is None:
        return None
    exercise_id, title = top
    rows = await _strength_points(
        session, user_id=user_id, exercise_id=exercise_id, since=since
    )
    return _build_strength_progress(
        title=title, rows=rows, window_start=since.date()
    )


async def build_overview(
    session: AsyncSession, *, user_id: uuid.UUID
) -> OverviewResponse:
    today = datetime.now(UTC)
    start_month = datetime.combine(_month_start(today.date()), datetime.min.time(), UTC)
    start_prev = datetime.combine(_prev_month_start(today.date()), datetime.min.time(), UTC)

    workouts_count = await _workouts_count(
        session, user_id=user_id, start=start_month, end=today
    )
    tonnage_now = await _tonnage_for_period(
        session, user_id=user_id, start=start_month, end=today
    )
    tonnage_prev = await _tonnage_for_period(
        session, user_id=user_id, start=start_prev, end=start_month
    )
    delta_percent = 0
    if tonnage_prev > 0:
        delta_percent = round((tonnage_now - tonnage_prev) / tonnage_prev * 100)

    streak = await _active_streak(session, user_id=user_id)

    metrics = OverviewMetrics(
        workouts_this_month=workouts_count,
        total_weight_kg=tonnage_now,
        total_weight_delta_percent=delta_percent,
        active_streak_days=streak,
        streak_is_personal_best=False,
    )

    strength = await _strength(session, user_id=user_id, now=today)

    recent = await _recent(session, user_id=user_id, limit=3)

    return OverviewResponse(
        month=start_month.date(),
        metrics=metrics,
        strength=strength,
        recent=recent,
    )


# Жёсткая отметка для импорта в API-роутер
__all__ = ["StrengthPoint", "build_overview"]
