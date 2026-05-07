"""Чистая логика прогноза InBody — spec 008.

Структура:
- `features.py` — сборка снапшота фичей (без БД).
- `baseline.py` — линейная регрессия по тренду InBody.
- `cold_start.py` — fallback для пользователей с <4 InBody.
- `predictor.py` — главный entry point: build_forecast.
- `interpretation.py` — rule-based текст.
- `evaluation.py` — сравнение прогноз/факт.

ML-модель (gradient boosting / RNN) подменяется в predictor.py через
переменную окружения; baseline остаётся как fallback (REQ-12).
"""

from .baseline import linear_fit, linear_forecast
from .cold_start import cold_start_forecast
from .evaluation import evaluate_forecast
from .features import (
    FeatureSnapshot,
    InBodyPoint,
    TrainingAggregate,
    build_feature_snapshot,
)
from .interpretation import build_interpretation
from .predictor import (
    ForecastBundle,
    ForecastMetricSeries,
    ForecastPoint,
    Override,
    PredictorInput,
    build_forecast,
)

__all__ = [
    "FeatureSnapshot",
    "ForecastBundle",
    "ForecastMetricSeries",
    "ForecastPoint",
    "InBodyPoint",
    "Override",
    "PredictorInput",
    "TrainingAggregate",
    "build_feature_snapshot",
    "build_forecast",
    "build_interpretation",
    "cold_start_forecast",
    "evaluate_forecast",
    "linear_fit",
    "linear_forecast",
]
