"""Unit-тесты pure-helpers «прогресс по цели» — spec 010 §3 Scenario 3.

Здесь только арифметика: проценты и интерполяция ETA. БД и forecast.service
дёргаются в integration-тестах.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.analytics import compute_eta, compute_progress

# ---------------------------------------------------------------------------
# compute_progress
# ---------------------------------------------------------------------------


class TestComputeProgressWeightLoss:
    def test_half_done(self) -> None:
        # 90 → 85 при цели 80 = 50%.
        result = compute_progress(
            start_value=90, current_value=85, target_value=80, goal="weight_loss"
        )
        assert result.progress_percent == 50
        assert result.already_reached is False

    def test_just_started(self) -> None:
        result = compute_progress(
            start_value=90, current_value=90, target_value=80, goal="weight_loss"
        )
        assert result.progress_percent == 0

    def test_exact_target_marked_reached(self) -> None:
        result = compute_progress(
            start_value=90, current_value=80, target_value=80, goal="weight_loss"
        )
        assert result.progress_percent == 100
        assert result.already_reached is True

    def test_overshoot_clamped(self) -> None:
        # Похудел сильнее цели — bar не превышает 100, но reached=True.
        result = compute_progress(
            start_value=90, current_value=78, target_value=80, goal="weight_loss"
        )
        assert result.progress_percent == 100
        assert result.already_reached is True

    def test_regress_clamped_to_zero(self) -> None:
        # Поправился — отрицательный прогресс прячем, чтобы не показывать «-20%».
        result = compute_progress(
            start_value=90, current_value=92, target_value=80, goal="weight_loss"
        )
        assert result.progress_percent == 0
        assert result.already_reached is False


class TestComputeProgressMuscleGain:
    def test_half_done(self) -> None:
        # 30 → 32.5 при цели 35 = 50%.
        result = compute_progress(
            start_value=30, current_value=32.5, target_value=35, goal="muscle_gain"
        )
        assert result.progress_percent == 50

    def test_already_reached(self) -> None:
        result = compute_progress(
            start_value=30, current_value=36, target_value=35, goal="muscle_gain"
        )
        assert result.progress_percent == 100
        assert result.already_reached is True


class TestComputeProgressDegenerate:
    def test_zero_distance_returns_100(self) -> None:
        # start == target — нечего считать. Безопасный фолбэк, не ZeroDivision.
        result = compute_progress(
            start_value=80, current_value=80, target_value=80, goal="weight_loss"
        )
        assert result.progress_percent == 100
        assert result.already_reached is True


# ---------------------------------------------------------------------------
# compute_eta
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _FP:
    """Подделка ForecastPoint для unit-теста (избегаем импорта из spec 008)."""

    horizon_weeks: int
    point: float


class TestComputeEtaWeightLoss:
    def test_first_point_already_below_target(self) -> None:
        # Если первая прогнозная точка уже ниже target — ETA = эта точка.
        eta = compute_eta(
            points=[_FP(1, 79.0)],
            target_value=80,
            goal="weight_loss",
            anchor_date=date(2026, 5, 1),
        )
        assert eta == date(2026, 5, 8)

    def test_interpolation_between_points(self) -> None:
        # Между неделями 4 и 8 пересекаем 80 (84 → 76); линейно ровно
        # посередине → +2 недели от 4-й, итого +6 недель.
        eta = compute_eta(
            points=[_FP(1, 89.0), _FP(4, 84.0), _FP(8, 76.0)],
            target_value=80,
            goal="weight_loss",
            anchor_date=date(2026, 1, 1),
        )
        assert eta == date(2026, 1, 1) + (date(2026, 2, 12) - date(2026, 1, 1))

    def test_target_unreachable_in_horizon(self) -> None:
        # Все точки выше target — ETA None, UI не показывает «через 6 мес».
        eta = compute_eta(
            points=[_FP(1, 89.0), _FP(4, 87.0), _FP(12, 84.0)],
            target_value=80,
            goal="weight_loss",
            anchor_date=date(2026, 1, 1),
        )
        assert eta is None

    def test_empty_points_return_none(self) -> None:
        eta = compute_eta(
            points=[],
            target_value=80,
            goal="weight_loss",
            anchor_date=date(2026, 1, 1),
        )
        assert eta is None

    def test_unsorted_points_handled(self) -> None:
        # Сервис может прислать unsorted (паранойя) — алгоритм всё равно
        # работает, потому что мы сортируем внутри.
        eta = compute_eta(
            points=[_FP(8, 76.0), _FP(1, 89.0), _FP(4, 84.0)],
            target_value=80,
            goal="weight_loss",
            anchor_date=date(2026, 1, 1),
        )
        assert eta is not None
        assert eta > date(2026, 1, 1) + (date(2026, 1, 29) - date(2026, 1, 1))


class TestComputeEtaMuscleGain:
    def test_basic_crossing(self) -> None:
        # 30 → 32 → 36 при target 35: пересечение между 4 и 8 неделями,
        # ровно 3/4 пути → 4 + 0.75*(8-4) = 7 недель.
        eta = compute_eta(
            points=[_FP(1, 30.5), _FP(4, 32.0), _FP(8, 36.0)],
            target_value=35,
            goal="muscle_gain",
            anchor_date=date(2026, 1, 1),
        )
        assert eta == date(2026, 1, 1) + (date(2026, 2, 19) - date(2026, 1, 1))

    def test_first_point_above_target(self) -> None:
        eta = compute_eta(
            points=[_FP(1, 36.0)],
            target_value=35,
            goal="muscle_gain",
            anchor_date=date(2026, 5, 1),
        )
        assert eta == date(2026, 5, 8)
