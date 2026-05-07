"""Тесты сравнения прогноза с фактом — spec 008 Scenario 3, SC-01..04."""

import pytest

from app.domain.forecast.evaluation import evaluate_forecast


class TestEvaluateForecast:
    def test_actual_inside_ci_marks_within(self) -> None:
        result = evaluate_forecast(
            point=78.0, ci_low=77.0, ci_high=79.0, actual=78.3
        )

        assert result.within_ci is True
        assert result.absolute_error == pytest.approx(0.3)

    def test_actual_outside_ci_marks_miss(self) -> None:
        result = evaluate_forecast(
            point=78.0, ci_low=77.0, ci_high=79.0, actual=80.5
        )

        assert result.within_ci is False
        assert result.absolute_error == pytest.approx(2.5)

    def test_actual_on_boundary_counts_as_within(self) -> None:
        # Граничные значения включительно — иначе coverage будет
        # систематически занижаться (важно для SC-03).
        result = evaluate_forecast(
            point=78.0, ci_low=77.0, ci_high=79.0, actual=77.0
        )

        assert result.within_ci is True
