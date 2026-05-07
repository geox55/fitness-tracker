"""Тесты линейного baseline-а — spec 008 §2 + REQ-12."""

import math

import pytest

from app.domain.forecast.baseline import (
    Z80,
    linear_fit,
    linear_forecast,
    physiological_clip_kg,
)


class TestLinearFit:
    def test_perfect_line_zero_sigma(self) -> None:
        # y = 2x + 1 → slope=2, intercept=1, residual variance = 0.
        xs = [0.0, 1.0, 2.0, 3.0]
        ys = [1.0, 3.0, 5.0, 7.0]

        fit = linear_fit(xs, ys)

        assert fit.slope == pytest.approx(2.0)
        assert fit.intercept == pytest.approx(1.0)
        assert fit.sigma == pytest.approx(0.0)
        assert fit.span == 3.0
        assert fit.n == 4

    def test_single_point_returns_constant(self) -> None:
        fit = linear_fit([5.0], [42.0])

        assert fit.slope == 0.0
        assert fit.intercept == 42.0
        assert fit.sigma == 0.0
        assert fit.n == 1

    def test_two_points_have_no_sigma(self) -> None:
        # n=2 даёт идеальную подгонку, residual var формально 0/0 — мы возвращаем 0.
        fit = linear_fit([0.0, 1.0], [1.0, 3.0])

        assert fit.slope == pytest.approx(2.0)
        assert fit.sigma == 0.0

    def test_noisy_line_has_positive_sigma(self) -> None:
        xs = [0.0, 7.0, 14.0, 21.0]
        ys = [80.0, 79.4, 78.7, 78.5]

        fit = linear_fit(xs, ys)

        # Тренд явно отрицательный, σ маленький, но > 0.
        assert fit.slope < 0
        assert fit.sigma > 0
        assert fit.n == 4

    def test_constant_x_returns_zero_slope(self) -> None:
        # Все измерения в один день — экстраполировать нечем.
        fit = linear_fit([0.0, 0.0, 0.0], [70.0, 71.0, 72.0])

        assert fit.slope == 0.0
        # intercept — среднее
        assert fit.intercept == pytest.approx(71.0)

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="equal length"):
            linear_fit([0.0, 1.0], [1.0])

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            linear_fit([], [])


class TestLinearForecast:
    def test_zero_sigma_yields_point_only_ci(self) -> None:
        fit = linear_fit([0.0, 1.0, 2.0], [80.0, 79.0, 78.0])

        point, lo, hi = linear_forecast(fit, x_target=10.0)

        assert point == pytest.approx(70.0)
        # Идеальная линия → CI вырождается в точку.
        assert lo == pytest.approx(point)
        assert hi == pytest.approx(point)

    def test_ci_widens_with_distance(self) -> None:
        # шумная серия
        xs = [0.0, 7.0, 14.0, 21.0]
        ys = [80.0, 78.5, 79.5, 78.0]
        fit = linear_fit(xs, ys)

        _, lo_near, hi_near = linear_forecast(fit, x_target=21.0)
        _, lo_far, hi_far = linear_forecast(fit, x_target=49.0)

        width_near = hi_near - lo_near
        width_far = hi_far - lo_far
        assert width_far > width_near

    def test_ci_z_constant_value(self) -> None:
        # Z80 ≈ 1.282 (Φ⁻¹(0.9))
        assert pytest.approx(1.2815515655446004, rel=1e-6) == Z80
        # Для известного σ можно прикинуть полуширину CI на хвосте наблюдений
        # (distance_norm = 0): ~ z·σ.
        xs = [0.0, 1.0, 2.0, 3.0]
        ys = [10.0, 11.0, 9.0, 12.0]
        fit = linear_fit(xs, ys)
        _point, lo, hi = linear_forecast(fit, x_target=3.0)
        half = (hi - lo) / 2
        # Z80·σ — ожидаемая половина CI на хвосте наблюдений.
        assert half == pytest.approx(Z80 * fit.sigma, rel=1e-6)

    def test_ci_bracket_invariants(self) -> None:
        fit = linear_fit([0.0, 7.0, 14.0], [80.0, 78.0, 76.0])
        point, lo, hi = linear_forecast(fit, x_target=28.0)

        assert lo <= point <= hi
        assert math.isfinite(point) and math.isfinite(lo) and math.isfinite(hi)


class TestPhysiologicalClip:
    def test_clip_positive_excess(self) -> None:
        # base=80, point=90 (+10 кг за 2 нед — нереально), max=1.5/нед → cap=3.
        clipped = physiological_clip_kg(80.0, 90.0, horizon_weeks=2)
        assert clipped == pytest.approx(83.0)

    def test_clip_negative_excess(self) -> None:
        clipped = physiological_clip_kg(80.0, 70.0, horizon_weeks=2)
        assert clipped == pytest.approx(77.0)

    def test_within_cap_unchanged(self) -> None:
        clipped = physiological_clip_kg(80.0, 78.0, horizon_weeks=2)
        assert clipped == pytest.approx(78.0)

    def test_custom_max_per_week(self) -> None:
        # body_fat: 1%/нед
        clipped = physiological_clip_kg(
            25.0, 28.0, horizon_weeks=2, max_per_week=1.0
        )
        assert clipped == pytest.approx(27.0)
