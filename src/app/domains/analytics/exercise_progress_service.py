"""Сервис прогресса по конкретному упражнению — spec 010 REQ-09.

Эндпоинт `/analytics/exercise-progress?exercise_id=...` — это «лучший
рабочий вес × неделя» и «лучший оценочный 1RM × неделя» для одного
упражнения пользователя. Чистая часть в `domain.analytics.exercise_progress`;
здесь — только БД-обвязка:

- проверяем, что exercise существует (если нет → `ExerciseNotFoundError`);
- читаем title (предпочитаем русское имя) для UI;
- грузим `(log_date, weight, reps)` non-skipped логов пользователя
  в диапазоне дат и передаём в `build_exercise_progress`.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import NamedTuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.analytics import (
    ExerciseProgressWeek,
    build_exercise_progress,
)
from ..catalog.models import Exercise
from ..workouts.models import ExerciseLog, Workout


class ExerciseAnalyticsError(Exception):
    code: str = "exercise_analytics_error"


class ExerciseNotFoundError(ExerciseAnalyticsError):
    """Упражнение с таким id не существует в каталоге."""

    code = "exercise_not_found"


_COMPLETED_STATUSES = ("completed", "auto_finished")


class ExerciseProgressResult(NamedTuple):
    exercise_id: uuid.UUID
    exercise_title: str | None
    weeks: list[ExerciseProgressWeek]


async def exercise_progress(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    exercise_id: uuid.UUID,
    from_: datetime | None = None,
    to: datetime | None = None,
) -> ExerciseProgressResult:
    """Собрать недельный прогресс пользователя по одному упражнению.

    `exercise_id` — глобальный (каталог общий для всех), но логи фильтруются
    по `user_id`. Если у юзера нет ни одного non-skipped лога — `weeks=[]`,
    UI покажет empty state. Заметь: 404 не уместен, у пользователя законно
    может не быть истории по упражнению.
    """
    ex = await session.get(Exercise, exercise_id)
    if ex is None:
        raise ExerciseNotFoundError(f"exercise {exercise_id} not found")
    title = ex.exercise_name_ru or ex.exercise_name

    log_date = Workout.performed_at  # ORDER BY-источник; группируем по дате лога
    stmt = (
        select(
            log_date.label("performed_at"),
            ExerciseLog.weight_kg,
            ExerciseLog.reps,
        )
        .join(Workout, Workout.id == ExerciseLog.workout_id)
        .where(
            Workout.user_id == user_id,
            Workout.status.in_(_COMPLETED_STATUSES),
            ExerciseLog.exercise_id == exercise_id,
            ExerciseLog.skipped.is_(False),
        )
    )
    if from_ is not None:
        stmt = stmt.where(Workout.performed_at >= from_)
    if to is not None:
        stmt = stmt.where(Workout.performed_at <= to)

    rows: list[tuple[date, float, int]] = [
        (row.performed_at.date(), float(row.weight_kg), int(row.reps))
        for row in (await session.execute(stmt)).all()
    ]
    weeks = build_exercise_progress(rows=rows)
    return ExerciseProgressResult(
        exercise_id=exercise_id, exercise_title=title, weeks=weeks
    )


__all__ = [
    "ExerciseAnalyticsError",
    "ExerciseNotFoundError",
    "ExerciseProgressResult",
    "exercise_progress",
]
