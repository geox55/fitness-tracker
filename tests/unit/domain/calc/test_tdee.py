"""Tests for TDEE (Total Daily Energy Expenditure) — spec 007.

TDEE = BMR * activity_multiplier(training_frequency)

Activity multipliers (spec 007 REQ-02):
    2 sessions/wk      → 1.375
    3-4 sessions/wk    → 1.55
    5-6 sessions/wk    → 1.725
"""

import pytest

from app.domain.calc.tdee import tdee


class TestTdee:
    @pytest.mark.parametrize(
        ("frequency", "expected_multiplier"),
        [
            (2, 1.375),
            (3, 1.55),
            (4, 1.55),
            (5, 1.725),
            (6, 1.725),
        ],
    )
    def test_multiplier_by_training_frequency(
        self, frequency: int, expected_multiplier: float
    ) -> None:
        bmr = 2000.0
        assert tdee(bmr_kcal=bmr, training_frequency=frequency) == pytest.approx(
            bmr * expected_multiplier
        )

    @pytest.mark.parametrize("frequency", [0, 1, 7, -1])
    def test_unsupported_frequency_raises(self, frequency: int) -> None:
        with pytest.raises(ValueError, match="training_frequency"):
            tdee(bmr_kcal=2000, training_frequency=frequency)
