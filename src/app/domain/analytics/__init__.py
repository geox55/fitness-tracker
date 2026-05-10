"""Чистая логика аналитики — spec 010.

Только pure-функции (без I/O и БД): селекторы метрик, расчёт дельт между
двумя замерами, проекция forecast-bundle на абсолютные даты для overlay
на графиках.

Сервис (`domains/analytics/service.py`) загружает данные из БД и
комбинирует их через эти helpers.
"""

from .goal_progress import (
    EtaConfidence,
    GoalCalc,
    GoalKind,
    compute_eta,
    compute_progress,
)
from .inbody_series import (
    COMPARABLE_FIELDS,
    FORECASTABLE_METRICS,
    SERIES_METRICS,
    DatedForecastPoint,
    FieldDelta,
    SeriesMetric,
    compute_deltas,
    forecast_to_dated_points,
    select_metric,
)

__all__ = [
    "COMPARABLE_FIELDS",
    "FORECASTABLE_METRICS",
    "SERIES_METRICS",
    "DatedForecastPoint",
    "EtaConfidence",
    "FieldDelta",
    "GoalCalc",
    "GoalKind",
    "SeriesMetric",
    "compute_deltas",
    "compute_eta",
    "compute_progress",
    "forecast_to_dated_points",
    "select_metric",
]
