"""Тесты главного entry point предиктора — spec 008 acceptance criteria."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.forecast.features import (
    InBodyPoint,
    TrainingAggregate,
    build_feature_snapshot,
)
from app.domain.forecast.predictor import (
    DEFAULT_HORIZONS,
    MODEL_VERSION_BASELINE,
    NotEnoughDataError,
    Override,
    PredictorInput,
    build_forecast,
)


def _ib(
    days_ago: int,
    *,
    weight: float = 80.0,
    fat: float = 22.0,
    muscle: float | None = 35.0,
    now: datetime | None = None,
) -> InBodyPoint:
    base = now or datetime(2026, 5, 1, tzinfo=UTC)
    return InBodyPoint(
        measured_at=base - timedelta(days=days_ago),
        weight_kg=weight,
        body_fat_percent=fat,
        muscle_mass_kg=muscle,
    )


def _make_snapshot(
    history: list[InBodyPoint],
    *,
    now: datetime,
    goal: str | None = "weight_loss",
    training_frequency: int | None = 3,
    trainings_8w: int = 12,
    goal_changed: int | None = None,
):
    weeks: list[TrainingAggregate] = []
    if trainings_8w > 0:
        # Раскидываем поровну по последним 4 неделям, чтобы попало в окно 8 недель.
        per_week = max(1, trainings_8w // 4)
        for w in range(4):
            weeks.append(
                TrainingAggregate(
                    week_start=now - timedelta(weeks=w),
                    tonnage_kg=1000,
                    count=per_week,
                    avg_duration_min=45,
                )
            )
    return build_feature_snapshot(
        inbody_history=history,
        training_weeks=weeks,
        goal=goal,  # type: ignore[arg-type]
        training_frequency=training_frequency,
        goal_changed_within_days=goal_changed,
        now=now,
    )


# ---------------------------------------------------------------------------
# Scenario 1 — high-confidence у пользователя с историей
# ---------------------------------------------------------------------------


class TestHighConfidenceScenario:
    """≥4 InBody, ≥8 тренировок за 8 нед, последний InBody ≤14 дней — high."""

    def test_returns_three_metrics_three_horizons(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, fat=22.0, muscle=35.0, now=now),
            _ib(21, weight=79.5, fat=21.7, muscle=35.1, now=now),
            _ib(14, weight=79.0, fat=21.4, muscle=35.2, now=now),
            _ib(7, weight=78.5, fat=21.1, muscle=35.3, now=now),
        ]
        snap = _make_snapshot(history, now=now)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        assert bundle.confidence == "high"
        assert bundle.fallback is False
        assert bundle.what_if is False
        assert bundle.model_version == MODEL_VERSION_BASELINE
        assert len(bundle.weight_kg.points) == len(DEFAULT_HORIZONS)
        assert len(bundle.body_fat_percent.points) == len(DEFAULT_HORIZONS)
        assert len(bundle.muscle_mass_kg.points) == len(DEFAULT_HORIZONS)

    def test_ci_low_le_point_le_ci_high(self) -> None:
        """Acceptance §3.1: точка + 80%-CI."""
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=79.5, now=now),
            _ib(14, weight=79.0, now=now),
            _ib(7, weight=78.7, now=now),
        ]
        snap = _make_snapshot(history, now=now)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        for series in (
            bundle.weight_kg,
            bundle.body_fat_percent,
            bundle.muscle_mass_kg,
        ):
            for p in series.points:
                assert p.ci_low <= p.point <= p.ci_high

    def test_downward_trend_predicts_lower_weight(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=79.5, now=now),
            _ib(14, weight=79.0, now=now),
            _ib(7, weight=78.5, now=now),
        ]
        snap = _make_snapshot(history, now=now)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        last = next(p for p in bundle.weight_kg.points if p.horizon_weeks == 4)
        assert last.point < 78.5

    def test_interpretation_mentions_horizon(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=79.5, now=now),
            _ib(14, weight=79.0, now=now),
            _ib(7, weight=78.5, now=now),
        ]
        snap = _make_snapshot(history, now=now)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        assert "4 недели" in bundle.interpretation


# ---------------------------------------------------------------------------
# Scenario 2 — cold start
# ---------------------------------------------------------------------------


class TestColdStart:
    def test_one_inbody_returns_low_confidence(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        snap = _make_snapshot(
            [_ib(0, weight=80.0, now=now)],
            now=now,
            trainings_8w=0,
        )

        bundle = build_forecast(PredictorInput(snapshot=snap))

        assert bundle.confidence == "low"
        assert "точнее" in bundle.interpretation

    def test_three_inbody_falls_under_cold_start(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(14, weight=80.0, now=now),
            _ib(7, weight=79.5, now=now),
            _ib(0, weight=79.0, now=now),
        ]
        snap = _make_snapshot(history, now=now)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        # Cold-start логика идёт по типичной траектории по goal=weight_loss
        # (Δ −0.5 кг/нед), а не по линейной регрессии.
        last = next(p for p in bundle.weight_kg.points if p.horizon_weeks == 4)
        assert last.point == pytest.approx(79.0 - 0.5 * 4, abs=0.05)

    def test_zero_inbody_raises(self) -> None:
        snap = _make_snapshot([], now=datetime(2026, 5, 1, tzinfo=UTC))

        with pytest.raises(NotEnoughDataError):
            build_forecast(PredictorInput(snapshot=snap))


# ---------------------------------------------------------------------------
# Confidence rules — REQ-04 + Edge cases §10
# ---------------------------------------------------------------------------


class TestConfidence:
    def test_old_last_inbody_drops_to_low(self) -> None:
        # Последний замер 70 дней назад → low.
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(120, weight=80.0, now=now),
            _ib(100, weight=80.0, now=now),
            _ib(80, weight=80.0, now=now),
            _ib(70, weight=80.0, now=now),
        ]
        snap = _make_snapshot(history, now=now, trainings_8w=12)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        assert bundle.confidence == "low"

    def test_recent_goal_change_caps_at_medium(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=79.5, now=now),
            _ib(14, weight=79.0, now=now),
            _ib(7, weight=78.5, now=now),
        ]
        snap = _make_snapshot(history, now=now, goal_changed=10)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        assert bundle.confidence == "medium"

    def test_few_trainings_drops_to_medium(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=79.5, now=now),
            _ib(14, weight=79.0, now=now),
            _ib(7, weight=78.5, now=now),
        ]
        snap = _make_snapshot(history, now=now, trainings_8w=2)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        assert bundle.confidence == "medium"


# ---------------------------------------------------------------------------
# What-if (Scenario 4)
# ---------------------------------------------------------------------------


class TestWhatIf:
    def test_calorie_deficit_lowers_weight_forecast(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=80.0, now=now),
            _ib(14, weight=80.0, now=now),
            _ib(7, weight=80.0, now=now),
        ]
        snap = _make_snapshot(history, now=now, training_frequency=3)

        baseline = build_forecast(PredictorInput(snapshot=snap))
        what_if = build_forecast(
            PredictorInput(
                snapshot=snap,
                override=Override(calories_offset_kcal=-500),
            )
        )

        baseline_w4 = next(
            p for p in baseline.weight_kg.points if p.horizon_weeks == 4
        )
        what_if_w4 = next(
            p for p in what_if.weight_kg.points if p.horizon_weeks == 4
        )
        assert what_if.what_if is True
        # Дефицит ⇒ what-if прогноз должен быть ниже.
        assert what_if_w4.point < baseline_w4.point

    def test_more_trainings_lowers_weight_forecast(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=80.0, now=now),
            _ib(14, weight=80.0, now=now),
            _ib(7, weight=80.0, now=now),
        ]
        snap = _make_snapshot(history, now=now, training_frequency=3)

        what_if = build_forecast(
            PredictorInput(
                snapshot=snap,
                override=Override(training_frequency=5),
            )
        )

        baseline = build_forecast(PredictorInput(snapshot=snap))
        a = next(p for p in what_if.weight_kg.points if p.horizon_weeks == 4)
        b = next(p for p in baseline.weight_kg.points if p.horizon_weeks == 4)
        assert a.point < b.point


# ---------------------------------------------------------------------------
# REQ-12: fallback
# ---------------------------------------------------------------------------


class TestFallback:
    def test_force_baseline_marks_fallback_true(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        history = [
            _ib(28, weight=80.0, now=now),
            _ib(21, weight=79.5, now=now),
            _ib(14, weight=79.0, now=now),
            _ib(7, weight=78.5, now=now),
        ]
        snap = _make_snapshot(history, now=now)

        bundle = build_forecast(
            PredictorInput(snapshot=snap, force_baseline=True)
        )

        assert bundle.fallback is True
        assert "Использован базовый расчёт" in bundle.interpretation


# ---------------------------------------------------------------------------
# Edge case §10 — физиологический клиппинг
# ---------------------------------------------------------------------------


class TestClipping:
    def test_extreme_downtrend_clamped_to_max_per_week(self) -> None:
        now = datetime(2026, 5, 1, tzinfo=UTC)
        # Дикий тренд: -3 кг/неделю. Должен быть обрезан до -1.5 кг/неделю.
        history = [
            _ib(28, weight=92.0, now=now),
            _ib(21, weight=89.0, now=now),
            _ib(14, weight=86.0, now=now),
            _ib(7, weight=83.0, now=now),
        ]
        snap = _make_snapshot(history, now=now)

        bundle = build_forecast(PredictorInput(snapshot=snap))

        last = next(p for p in bundle.weight_kg.points if p.horizon_weeks == 4)
        # base=83, cap=-1.5*4=-6 ⇒ point >= 83-6=77.
        assert last.point >= 77.0
