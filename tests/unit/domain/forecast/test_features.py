"""Тесты сборки фичей предиктора — spec 008 §2."""

from datetime import UTC, datetime, timedelta

from app.domain.forecast.features import (
    InBodyPoint,
    TrainingAggregate,
    build_feature_snapshot,
    serialize_features,
)


def _ib(days_ago: int, *, weight: float = 80.0, fat: float = 22.0) -> InBodyPoint:
    return InBodyPoint(
        measured_at=datetime.now(UTC) - timedelta(days=days_ago),
        weight_kg=weight,
        body_fat_percent=fat,
        muscle_mass_kg=35.0,
    )


class TestBuildFeatureSnapshot:
    def test_history_sorted_ascending(self) -> None:
        snap = build_feature_snapshot(
            inbody_history=[_ib(0), _ib(30), _ib(15)],
            now=datetime.now(UTC),
        )

        days = [
            (datetime.now(UTC) - p.measured_at).days for p in snap.inbody_history
        ]
        # ASC по measured_at == DESC по days_ago
        assert days == sorted(days, reverse=True)

    def test_latest_is_last_in_sorted_history(self) -> None:
        snap = build_feature_snapshot(
            inbody_history=[_ib(30, weight=82.0), _ib(0, weight=78.0)],
            now=datetime.now(UTC),
        )

        assert snap.latest is not None
        assert snap.latest.weight_kg == 78.0

    def test_empty_history_no_latest(self) -> None:
        snap = build_feature_snapshot(
            inbody_history=[], now=datetime.now(UTC)
        )

        assert snap.latest is None
        assert snap.history_span_days == 0
        assert snap.last_inbody_age_days is None

    def test_history_span_days(self) -> None:
        snap = build_feature_snapshot(
            inbody_history=[_ib(28), _ib(0)], now=datetime.now(UTC)
        )

        assert snap.history_span_days == 28

    def test_trainings_last_8w_filters_old_weeks(self) -> None:
        now = datetime.now(UTC)
        weeks = [
            TrainingAggregate(
                week_start=now - timedelta(weeks=10),
                tonnage_kg=1000,
                count=3,
                avg_duration_min=45,
            ),
            TrainingAggregate(
                week_start=now - timedelta(weeks=2),
                tonnage_kg=1500,
                count=4,
                avg_duration_min=50,
            ),
        ]
        snap = build_feature_snapshot(
            inbody_history=[_ib(0)],
            training_weeks=weeks,
            now=now,
        )

        # Старая неделя обрезана.
        assert snap.trainings_last_8w == 4


class TestSerializeFeatures:
    def test_keys_present_for_audit(self) -> None:
        snap = build_feature_snapshot(
            inbody_history=[_ib(28), _ib(0)],
            goal="weight_loss",
            training_frequency=4,
            sex="female",
            now=datetime.now(UTC),
        )

        slate = serialize_features(snap)

        assert slate["n_inbody"] == 2
        assert slate["history_span_days"] == 28
        assert slate["goal"] == "weight_loss"
        assert slate["training_frequency"] == 4
        assert slate["sex"] == "female"
        # Эти поля должны быть всегда — для воспроизводимости (NFR-04).
        for k in ("trainings_last_8w", "last_inbody_age_days"):
            assert k in slate
