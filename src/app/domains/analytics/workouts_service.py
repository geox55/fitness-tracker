"""Аналитика тренировок — БД-обвязка для spec 010 §3 Scenario 4 (REQ-07/08).

Возвращает агрегаты по периодам (неделя/месяц/день):
- `tonnage_kg` = SUM(reps * weight_kg) по non-skipped logs;
- `workouts_count` = COUNT(DISTINCT workout_id) среди завершённых.

Почему один SQL с LEFT JOIN, а не два запроса:
- workout без логов всё равно идёт в счётчик (счётчик «провёл день в зале»);
- left-join'енный фильтр `skipped=false` отсеивает пропущенные сеты, но
  оставляет workout в COUNT(DISTINCT);
- группа `date_trunc(bucket, performed_at)` гарантирует, что неделя
  показана даже если в ней не было ни одного лога.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Literal

from sqlalchemy import Function, and_, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..workouts.models import ExerciseLog, Workout

Bucket = Literal["day", "week", "month"]
SUPPORTED_BUCKETS: tuple[str, ...] = ("day", "week", "month")

# Только эти статусы считаем «состоявшейся тренировкой»: in_progress —
# юзер прервал, cancelled — отменил вручную. Совпадает с фильтром
# в analytics.service.build_overview, чтобы цифры на главном экране
# и в детальной аналитике сходились.
_COMPLETED_STATUSES = ("completed", "auto_finished")


class AnalyticsWorkoutsError(Exception):
    code: str = "analytics_workouts_error"


class UnsupportedBucketError(AnalyticsWorkoutsError):
    code = "unsupported_bucket"


def _truncate(bucket: str, column: Any) -> Function[Any]:
    """`date_trunc('week', performed_at)` → SQLAlchemy expression.

    Whitelist на bucket — обязателен; param. сюда попадает прямо в SQL
    как литерал (date_trunc первый аргумент должен быть строкой).
    """
    if bucket not in SUPPORTED_BUCKETS:
        raise UnsupportedBucketError(
            f"unsupported bucket: {bucket!r}; allowed: {SUPPORTED_BUCKETS}"
        )
    return func.date_trunc(bucket, column)


async def workouts_buckets(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    bucket: str,
    from_: datetime | None = None,
    to: datetime | None = None,
) -> list[tuple[date, float, int]]:
    """Список (period_start, tonnage_kg, workouts_count) в порядке возрастания.

    Возвращает пустой список, если у пользователя нет завершённых
    тренировок в диапазоне. `period_start` — date (не datetime), чтобы
    клиент рисовал ось X в днях.
    """
    if bucket not in SUPPORTED_BUCKETS:
        raise UnsupportedBucketError(
            f"unsupported bucket: {bucket!r}; allowed: {SUPPORTED_BUCKETS}"
        )

    period = _truncate(bucket, Workout.performed_at).label("period")
    tonnage = func.coalesce(
        func.sum(ExerciseLog.reps * ExerciseLog.weight_kg), 0
    ).label("tonnage")
    workouts_n = func.count(distinct(Workout.id)).label("workouts")

    join_on = and_(
        ExerciseLog.workout_id == Workout.id,
        ExerciseLog.skipped.is_(False),
    )

    stmt = (
        select(period, tonnage, workouts_n)
        .select_from(Workout)
        .outerjoin(ExerciseLog, join_on)
        .where(
            Workout.user_id == user_id,
            Workout.status.in_(_COMPLETED_STATUSES),
        )
        .group_by(period)
        .order_by(period)
    )
    if from_ is not None:
        stmt = stmt.where(Workout.performed_at >= from_)
    if to is not None:
        stmt = stmt.where(Workout.performed_at <= to)

    rows = (await session.execute(stmt)).all()
    return [
        (row.period.date() if isinstance(row.period, datetime) else row.period,
         float(row.tonnage),
         int(row.workouts))
        for row in rows
    ]
