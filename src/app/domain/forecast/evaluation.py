"""Сравнение прогноза с фактом — Scenario 3, метрики SC-01..04.

Чистая функция: на вход — прогнозная точка и фактическое значение,
на выход — `EvaluationResult`. БД-обвязка ищет подходящую пару
forecast/actual в service.py (примерно T+horizon ±3 дня по спеке).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    absolute_error: float
    within_ci: bool


def evaluate_forecast(
    *,
    point: float,
    ci_low: float,
    ci_high: float,
    actual: float,
) -> EvaluationResult:
    return EvaluationResult(
        absolute_error=abs(actual - point),
        within_ci=ci_low <= actual <= ci_high,
    )
