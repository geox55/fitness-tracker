"""Unit-тесты pure-helpers analytics — spec 010."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from app.domain.analytics import (
    COMPARABLE_FIELDS,
    FORECASTABLE_METRICS,
    SERIES_METRICS,
    compute_deltas,
    forecast_to_dated_points,
    select_metric,
)


@dataclass
class _Measurement:
    """Минимальный «duck-typed» аналог InBodyMeasurement для unit-тестов.

    select_metric/compute_deltas работают через getattr, так что нам не
    нужен настоящий ORM-класс — это держит тесты чистыми (без БД).
    """

    weight_kg: Decimal | None = None
    body_fat_percent: Decimal | None = None
    muscle_mass_kg: Decimal | None = None
    body_water_percent: Decimal | None = None
    protein_kg: Decimal | None = None
    minerals_kg: Decimal | None = None
    visceral_fat_level: int | None = None
    bmr_kcal: int | None = None
    fat_free_mass_kg: Decimal | None = None
    bmi: Decimal | None = None
    height_cm: Decimal | None = None


class TestSelectMetric:
    def test_decimal_value_returned_as_float(self) -> None:
        m = _Measurement(weight_kg=Decimal("78.5"))
        assert select_metric(m, "weight_kg") == 78.5

    def test_int_value_returned_as_float(self) -> None:
        m = _Measurement(bmr_kcal=1750)
        assert select_metric(m, "bmr_kcal") == 1750.0

    def test_none_value(self) -> None:
        m = _Measurement()
        assert select_metric(m, "muscle_mass_kg") is None

    def test_unknown_metric_raises(self) -> None:
        m = _Measurement()
        with pytest.raises(ValueError, match="unknown metric"):
            select_metric(m, "made_up_field")

    def test_all_series_metrics_work(self) -> None:
        # Контракт: все метрики из SERIES_METRICS должны быть атрибутами,
        # которые select_metric умеет читать. Защита от опечаток в SERIES_METRICS.
        m = _Measurement(
            weight_kg=Decimal("80"),
            body_fat_percent=Decimal("18"),
            muscle_mass_kg=Decimal("35"),
            body_water_percent=Decimal("55"),
            protein_kg=Decimal("12"),
            minerals_kg=Decimal("4"),
            visceral_fat_level=7,
            bmr_kcal=1800,
            fat_free_mass_kg=Decimal("65"),
            bmi=Decimal("25"),
            height_cm=Decimal("175"),
        )
        for metric in SERIES_METRICS:
            assert select_metric(m, metric) is not None


class TestComputeDeltas:
    def test_full_delta_for_each_field(self) -> None:
        a = _Measurement(weight_kg=Decimal("82.0"), body_fat_percent=Decimal("20.0"))
        b = _Measurement(weight_kg=Decimal("80.0"), body_fat_percent=Decimal("18.0"))

        deltas = {d.field: d for d in compute_deltas(a, b)}

        assert deltas["weight_kg"].value_a == 82.0
        assert deltas["weight_kg"].value_b == 80.0
        assert deltas["weight_kg"].delta_absolute == -2.0
        # -2/82 * 100 = -2.439... → -2.44 (round 2)
        assert deltas["weight_kg"].delta_percent == pytest.approx(-2.44, abs=0.01)

        assert deltas["body_fat_percent"].delta_absolute == -2.0
        assert deltas["body_fat_percent"].delta_percent == pytest.approx(-10.0)

    def test_missing_value_in_a_yields_no_delta(self) -> None:
        a = _Measurement()
        b = _Measurement(muscle_mass_kg=Decimal("35"))

        d = next(
            x for x in compute_deltas(a, b) if x.field == "muscle_mass_kg"
        )

        assert d.value_a is None
        assert d.value_b == 35.0
        assert d.delta_absolute is None
        assert d.delta_percent is None

    def test_missing_value_in_b_yields_no_delta(self) -> None:
        a = _Measurement(muscle_mass_kg=Decimal("35"))
        b = _Measurement()

        d = next(
            x for x in compute_deltas(a, b) if x.field == "muscle_mass_kg"
        )

        assert d.value_a == 35.0
        assert d.value_b is None
        assert d.delta_absolute is None

    def test_zero_baseline_does_not_divide(self) -> None:
        # Защита от ZeroDivisionError: если value_a == 0 — pct безопасно None.
        a = _Measurement(visceral_fat_level=0)
        b = _Measurement(visceral_fat_level=2)

        d = next(
            x for x in compute_deltas(a, b) if x.field == "visceral_fat_level"
        )

        assert d.delta_absolute == 2.0
        assert d.delta_percent is None

    def test_only_requested_fields_included(self) -> None:
        a = _Measurement(weight_kg=Decimal("82"), body_fat_percent=Decimal("18"))
        b = _Measurement(weight_kg=Decimal("80"), body_fat_percent=Decimal("17"))

        deltas = compute_deltas(a, b, fields=("weight_kg",))

        assert [d.field for d in deltas] == ["weight_kg"]

    def test_all_comparable_fields_returned_by_default(self) -> None:
        a = _Measurement()
        b = _Measurement()

        result = compute_deltas(a, b)

        assert tuple(d.field for d in result) == COMPARABLE_FIELDS


# ---------------------------------------------------------------------------
# forecast_to_dated_points
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _ForecastPoint:
    horizon_weeks: int
    point: float
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class _MetricSeries:
    points: tuple[_ForecastPoint, ...]


@dataclass(frozen=True)
class _Bundle:
    weight_kg: _MetricSeries
    body_fat_percent: _MetricSeries
    muscle_mass_kg: _MetricSeries


class TestForecastToDatedPoints:
    @pytest.fixture
    def bundle(self) -> _Bundle:
        return _Bundle(
            weight_kg=_MetricSeries(
                points=(
                    _ForecastPoint(1, 79.5, 78.5, 80.5),
                    _ForecastPoint(2, 79.0, 77.5, 80.5),
                    _ForecastPoint(4, 78.0, 76.0, 80.0),
                )
            ),
            body_fat_percent=_MetricSeries(
                points=(_ForecastPoint(1, 17.5, 16.5, 18.5),)
            ),
            muscle_mass_kg=_MetricSeries(points=()),
        )

    def test_horizon_weeks_become_dates(self, bundle: _Bundle) -> None:
        anchor = date(2026, 5, 1)
        points = forecast_to_dated_points(
            metric="weight_kg", bundle=bundle, anchor_date=anchor
        )

        assert len(points) == 3
        assert points[0].date == date(2026, 5, 8)   # +1 неделя
        assert points[1].date == date(2026, 5, 15)  # +2 недели
        assert points[2].date == date(2026, 5, 29)  # +4 недели

    def test_values_and_ci_passthrough(self, bundle: _Bundle) -> None:
        points = forecast_to_dated_points(
            metric="weight_kg", bundle=bundle, anchor_date=date(2026, 5, 1)
        )
        assert points[0].value == 79.5
        assert points[0].ci_low == 78.5
        assert points[0].ci_high == 80.5

    def test_non_forecastable_metric_returns_empty(self, bundle: _Bundle) -> None:
        # bmi нет в FORECASTABLE_METRICS — не должно дёргаться даже через
        # getattr на bundle (у него и нет такого поля).
        points = forecast_to_dated_points(
            metric="bmi", bundle=bundle, anchor_date=date(2026, 5, 1)
        )
        assert points == []

    def test_empty_series_returns_empty(self, bundle: _Bundle) -> None:
        points = forecast_to_dated_points(
            metric="muscle_mass_kg", bundle=bundle, anchor_date=date(2026, 5, 1)
        )
        assert points == []

    def test_forecastable_metrics_are_subset_of_series(self) -> None:
        # FORECASTABLE_METRICS должен быть строго подмножеством SERIES_METRICS,
        # иначе UI не сможет нарисовать сами data-точки под пунктиром.
        assert set(FORECASTABLE_METRICS).issubset(set(SERIES_METRICS))
