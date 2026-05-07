"""Тесты детектора изменения веса — REQ-01 + Scenario 1."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.adaptation.weight_watcher import (
    compute_delta,
    should_trigger,
)

NOW = datetime(2026, 5, 1, tzinfo=UTC)


def _delta(*, prev: float, new: float, days_between: int):
    prev_at = NOW - timedelta(days=days_between)
    return compute_delta(
        prev_weight_kg=prev,
        new_weight_kg=new,
        prev_measured_at=prev_at,
        new_measured_at=NOW,
    )


class TestComputeDelta:
    def test_signs_match(self) -> None:
        d = _delta(prev=80.0, new=78.0, days_between=14)

        assert d.delta_kg == pytest.approx(-2.0)
        assert d.delta_percent == pytest.approx(-2.5)
        assert d.days_between == 14

    def test_zero_weight_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            compute_delta(
                prev_weight_kg=0,
                new_weight_kg=80.0,
                prev_measured_at=NOW,
                new_measured_at=NOW,
            )


class TestShouldTrigger:
    def test_abs_threshold_kg(self) -> None:
        assert should_trigger(_delta(prev=80, new=82.5, days_between=60))

    def test_under_abs_threshold_long_window_no_trigger(self) -> None:
        # 1 кг за 60 дней — мелочь.
        assert not should_trigger(_delta(prev=80, new=81.0, days_between=60))

    def test_relative_threshold_within_30_days(self) -> None:
        # 3.5% за 14 дней — триггер по относительному правилу.
        assert should_trigger(_delta(prev=80, new=77.2, days_between=14))

    def test_relative_threshold_outside_window_no_trigger(self) -> None:
        # 3.5% за 35 дней — окно вышло, сработать может только абсолютный.
        # Δ=2.8 кг → срабатывает абсолютный (2.8 > 2.0).
        assert should_trigger(_delta(prev=80, new=77.2, days_between=35))
        # А вот 2.5% за 35 дней (1.0 кг → меньше абс) — не триггерит.
        assert not should_trigger(_delta(prev=80, new=78.0, days_between=35))

    def test_minor_change_no_trigger(self) -> None:
        # 0.5 кг = 0.6% — ничего не меняем.
        assert not should_trigger(_delta(prev=80, new=80.5, days_between=7))

    def test_negative_days_no_relative_trigger(self) -> None:
        # Защитимся от перепутанных дат: предыдущий замер позже нового.
        # Положимся только на абсолютную проверку.
        d = compute_delta(
            prev_weight_kg=80.0,
            new_weight_kg=83.0,
            prev_measured_at=NOW + timedelta(days=1),
            new_measured_at=NOW,
        )
        # Абсолютная разница 3 кг > 2 → триггерим.
        assert should_trigger(d)
