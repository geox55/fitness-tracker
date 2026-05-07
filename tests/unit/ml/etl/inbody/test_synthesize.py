"""Тесты синтезатора траекторий — REQ-16, ключевые свойства модели."""

import random
import statistics

from ml.etl.inbody.anchor import Anchor
from ml.etl.inbody.synthesize import synthesize_trajectory


def _anchor(**overrides) -> Anchor:
    base = {
        "raw_user_id": "u1",
        "source": "s3",
        "sex": "male",
        "age_years": 30,
        "height_cm": 175.0,
        "weight_kg": 80.0,
        "body_fat_percent": 22.0,
        "muscle_mass_kg": 35.0,
        "bmr_kcal": 1700.0,
        "training_frequency_per_week": 3,
    }
    base.update(overrides)
    return Anchor(**base)


class TestSynthesizeTrajectory:
    def test_returns_weeks_rows(self) -> None:
        rng = random.Random(0)

        rows = synthesize_trajectory(
            _anchor(), anon_user_id="anon", weeks=8, rng=rng
        )

        assert len(rows) == 8
        assert [r.t_week for r in rows] == list(range(8))

    def test_first_row_matches_anchor(self) -> None:
        rng = random.Random(0)
        a = _anchor()

        rows = synthesize_trajectory(a, anon_user_id="anon", weeks=4, rng=rng)

        assert rows[0].weight_kg == round(a.weight_kg, 2)
        assert rows[0].body_fat_percent == round(a.body_fat_percent, 1)

    def test_target_t1_matches_next_row(self) -> None:
        rng = random.Random(0)

        rows = synthesize_trajectory(
            _anchor(), anon_user_id="anon", weeks=5, rng=rng
        )

        from itertools import pairwise

        for current, nxt in pairwise(rows):
            assert current.target_weight_t1 == nxt.weight_kg
            assert current.target_bf_t1 == nxt.body_fat_percent

    def test_weight_loss_trend_negative_on_average(self) -> None:
        # У anchor с BMI 26+ goal выводится в weight_loss → средний тренд вниз.
        a = _anchor(weight_kg=95, height_cm=175, body_fat_percent=28)
        diffs: list[float] = []
        for seed in range(50):
            rng = random.Random(seed)
            rows = synthesize_trajectory(
                a, anon_user_id=f"u{seed}", weeks=8, rng=rng
            )
            diffs.append(rows[-1].weight_kg - rows[0].weight_kg)

        # Медиана должна быть отрицательной.
        assert statistics.median(diffs) < 0

    def test_muscle_gain_trend_positive_on_average(self) -> None:
        a = _anchor(weight_kg=60, height_cm=180, body_fat_percent=12)
        diffs: list[float] = []
        for seed in range(50):
            rng = random.Random(seed)
            rows = synthesize_trajectory(
                a, anon_user_id=f"u{seed}", weeks=8, rng=rng
            )
            diffs.append(rows[-1].muscle_mass_kg - rows[0].muscle_mass_kg)

        assert statistics.median(diffs) > 0

    def test_physiological_clip_per_week(self) -> None:
        # Большая частота тренировок не должна выйти за ±1.5 кг/нед.
        rng = random.Random(0)
        a = _anchor(training_frequency_per_week=6)

        rows = synthesize_trajectory(
            a, anon_user_id="anon", weeks=20, rng=rng
        )

        from itertools import pairwise

        for prev, nxt in pairwise(rows):
            assert abs(nxt.weight_kg - prev.weight_kg) <= 1.5 + 1e-6

    def test_weeks_below_two_raises(self) -> None:
        rng = random.Random(0)
        try:
            synthesize_trajectory(
                _anchor(), anon_user_id="anon", weeks=1, rng=rng
            )
        except ValueError as exc:
            assert "weeks" in str(exc)
        else:
            raise AssertionError("expected ValueError")

    def test_deterministic_with_seed(self) -> None:
        rng_a = random.Random(123)
        rng_b = random.Random(123)

        rows_a = synthesize_trajectory(
            _anchor(), anon_user_id="anon", weeks=8, rng=rng_a
        )
        rows_b = synthesize_trajectory(
            _anchor(), anon_user_id="anon", weeks=8, rng=rng_b
        )

        assert [r.weight_kg for r in rows_a] == [r.weight_kg for r in rows_b]

    def test_muscle_mass_imputed_from_ffm_when_missing(self) -> None:
        rng = random.Random(0)
        a = _anchor(muscle_mass_kg=None)

        rows = synthesize_trajectory(a, anon_user_id="anon", weeks=4, rng=rng)

        # FFM = 80·(1−0.22) = 62.4; muscle ≈ 31.2
        assert rows[0].muscle_mass_kg is not None
        assert 25 < rows[0].muscle_mass_kg < 40
