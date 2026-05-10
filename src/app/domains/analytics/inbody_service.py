"""Аналитика InBody — БД-обвязка над `domain.analytics` — spec 010.

Здесь только две оркестрации поверх pure-helpers:
- `series` — вытащить из БД historic-точки по метрике в диапазоне дат и
  (для forecastable-метрик) подмешать прогноз из `forecast.service`.
- `compare` — вытащить два конкретных measurements пользователя и
  посчитать дельты через `compute_deltas`.

Поскольку эти запросы могут идти параллельно с расчётом прогноза,
используем уже существующий `get_forecast` (с его кэшем NFR-02 spec 008):
не реализуем своё кеширование.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.analytics import (
    COMPARABLE_FIELDS,
    DatedForecastPoint,
    FieldDelta,
    compute_deltas,
    forecast_to_dated_points,
    select_metric,
)
from ..forecast.service import NotEnoughInBodyError, get_forecast
from ..inbody.models import InBodyMeasurement


class AnalyticsError(Exception):
    code: str = "analytics_error"


class MeasurementNotFoundError(AnalyticsError):
    """compare: один из id не существует или принадлежит другому пользователю."""

    code = "measurement_not_found"


# ---------------------------------------------------------------------------
# Серия по метрике
# ---------------------------------------------------------------------------


async def _load_in_range(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    from_: datetime | None,
    to: datetime | None,
) -> list[InBodyMeasurement]:
    """Все измерения пользователя в [from_; to], отсортированные по времени.

    `from_/to` опциональны (REQ-02): без них возвращаем всю историю.
    Включаем границы по `>=`/`<=`, чтобы UI с диапазоном «1m=за месяц»
    совпадал с тем, что покажет график.
    """
    stmt = select(InBodyMeasurement).where(InBodyMeasurement.user_id == user_id)
    if from_ is not None:
        stmt = stmt.where(InBodyMeasurement.measured_at >= from_)
    if to is not None:
        stmt = stmt.where(InBodyMeasurement.measured_at <= to)
    stmt = stmt.order_by(InBodyMeasurement.measured_at.asc())
    return list((await session.execute(stmt)).scalars().all())


async def series(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    metric: str,
    from_: datetime | None = None,
    to: datetime | None = None,
    include_forecast: bool = True,
) -> tuple[list[tuple[date, float]], list[DatedForecastPoint]]:
    """Сходить за историей и (опц.) прогнозом.

    Возвращает пару:
    - history — list[(measured_at::date, value::float)] без None'ов;
      измерения, в которых нужное поле пропущено, фильтруем — на графике
      они выглядели бы как разрыв или нулевая точка.
    - forecast — list[DatedForecastPoint], пустой если:
        * include_forecast=False;
        * метрика не из FORECASTABLE_METRICS (см. spec 008);
        * прогноз не построился (NotEnoughInBodyError) — это не ошибка
          для analytics-эндпоинта: история показывается, пунктир — нет.
    """
    rows = await _load_in_range(session, user_id=user_id, from_=from_, to=to)
    history: list[tuple[date, float]] = []
    for row in rows:
        v = select_metric(row, metric)
        if v is None:
            continue
        history.append((row.measured_at.date(), v))

    if not include_forecast:
        return history, []

    try:
        bundle, _generated_at, based_on_id = await get_forecast(
            session, user_id=user_id
        )
    except NotEnoughInBodyError:
        return history, []

    # anchor — дата последнего измерения, на которое опирается прогноз.
    anchor = await session.get(InBodyMeasurement, based_on_id)
    if anchor is None:
        return history, []
    forecast = forecast_to_dated_points(
        metric=metric, bundle=bundle, anchor_date=anchor.measured_at.date()
    )
    return history, forecast


# ---------------------------------------------------------------------------
# Сравнение двух замеров
# ---------------------------------------------------------------------------


async def compare(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    a_id: uuid.UUID,
    b_id: uuid.UUID,
) -> tuple[InBodyMeasurement, InBodyMeasurement, list[FieldDelta]]:
    """Вернуть два измерения пользователя + дельты по сравнимым полям.

    Если хоть один id не найден или принадлежит другому пользователю —
    `MeasurementNotFoundError` (API → 404). user-фильтр обязателен — иначе
    утечёт сам факт существования чужого замера.
    """
    stmt = select(InBodyMeasurement).where(
        InBodyMeasurement.user_id == user_id,
        InBodyMeasurement.id.in_([a_id, b_id]),
    )
    rows = list((await session.execute(stmt)).scalars().all())
    by_id = {r.id: r for r in rows}
    if a_id not in by_id or b_id not in by_id:
        raise MeasurementNotFoundError(
            f"measurement not found: a={a_id} b={b_id}"
        )

    a, b = by_id[a_id], by_id[b_id]
    deltas = compute_deltas(a, b, fields=COMPARABLE_FIELDS)
    return a, b, deltas


# ---------------------------------------------------------------------------
# Парс/нормализация дат для query-параметров (используется API-слоем)
# ---------------------------------------------------------------------------


def to_datetime_inclusive_end(d: date | None) -> datetime | None:
    """`to=2026-04-30` → 2026-04-30 23:59:59.999999 UTC.

    Это включает измерения, сделанные в этот день. Без такого
    «расширения» SELECT `<= to` не вернул бы события дня `to`, потому что
    measured_at содержит время.
    """
    if d is None:
        return None
    return datetime(d.year, d.month, d.day, 23, 59, 59, 999_999, tzinfo=UTC)


def to_datetime_inclusive_start(d: date | None) -> datetime | None:
    if d is None:
        return None
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=UTC)


# Эти helpers переэкспортируем в workouts_service: те же даты/диапазоны,
# единый источник правды.
__all__ = [
    "AnalyticsError",
    "MeasurementNotFoundError",
    "compare",
    "series",
    "to_datetime_inclusive_end",
    "to_datetime_inclusive_start",
]
