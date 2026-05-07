"""Тесты impute / outliers — REQ-14 + Edge case §10."""

import pytest
from ml.etl.inbody.anchor import Anchor
from ml.etl.inbody.impute import (
    bmi,
    bmr_mifflin_st_jeor,
    filter_and_impute,
    impute_bmr,
    is_outlier,
)


def _anchor(**overrides) -> Anchor:
    base = {
        "raw_user_id": "u1",
        "source": "s3",
        "sex": "male",
        "age_years": 30,
        "height_cm": 175.0,
        "weight_kg": 75.0,
        "body_fat_percent": 18.0,
    }
    base.update(overrides)
    return Anchor(**base)


class TestBmi:
    def test_valid_values(self) -> None:
        assert bmi(75.0, 175.0) == pytest.approx(24.49, abs=0.01)

    def test_zero_height_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            bmi(75.0, 0)


class TestBmrFormula:
    def test_male_matches_canonical(self) -> None:
        # Пример из app.domain.calc.bmr — должны совпасть.
        assert bmr_mifflin_st_jeor(
            weight_kg=70, height_cm=175, age_years=30, sex="male"
        ) == pytest.approx(1648.75)

    def test_female_matches_canonical(self) -> None:
        assert bmr_mifflin_st_jeor(
            weight_kg=60, height_cm=165, age_years=28, sex="female"
        ) == pytest.approx(1330.25)

    def test_unknown_sex_raises(self) -> None:
        with pytest.raises(ValueError, match="sex"):
            bmr_mifflin_st_jeor(
                weight_kg=70, height_cm=175, age_years=30, sex="other"
            )


class TestIsOutlier:
    def test_normal_anchor_not_outlier(self) -> None:
        assert not is_outlier(_anchor())

    def test_extreme_low_bmi_dropped(self) -> None:
        assert is_outlier(_anchor(weight_kg=30, height_cm=200))

    def test_extreme_high_bmi_dropped(self) -> None:
        assert is_outlier(_anchor(weight_kg=200, height_cm=160))

    def test_impossible_body_fat_dropped(self) -> None:
        assert is_outlier(_anchor(body_fat_percent=80))
        assert is_outlier(_anchor(body_fat_percent=1))

    def test_under_age_dropped(self) -> None:
        assert is_outlier(_anchor(age_years=12))
        assert is_outlier(_anchor(age_years=95))


class TestImputeBmr:
    def test_fills_missing_bmr(self) -> None:
        anchor = _anchor()  # bmr_kcal=None
        result = impute_bmr(anchor)
        assert result.bmr_kcal is not None
        assert 1500 < result.bmr_kcal < 2000

    def test_keeps_existing_bmr(self) -> None:
        anchor = _anchor(bmr_kcal=1800.0)
        assert impute_bmr(anchor).bmr_kcal == 1800.0


class TestFilterAndImpute:
    def test_filters_outliers_and_imputes_bmr(self) -> None:
        anchors = [
            _anchor(),  # ok
            _anchor(raw_user_id="u2", body_fat_percent=80),  # outlier
            _anchor(raw_user_id="u3", bmr_kcal=1800.0),  # ok, no impute
        ]

        clean, stats = filter_and_impute(anchors)

        assert stats == {
            "input": 3, "outliers": 1, "imputed_bmr": 1, "kept": 2
        }
        assert all(a.bmr_kcal is not None for a in clean)
