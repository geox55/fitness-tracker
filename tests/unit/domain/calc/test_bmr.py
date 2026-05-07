"""Tests for BMR calculation (Mifflin-St Jeor formula).

Used by:
- spec 002 (UserProfile.bmr_kcal)
- spec 008 (forecast feature)
- spec 012-B (training dataset imputation)

Formula reference (Mifflin & St Jeor, 1990):
    male:   BMR = 10·weight + 6.25·height - 5·age + 5
    female: BMR = 10·weight + 6.25·height - 5·age - 161
"""

import pytest

from app.domain.calc.bmr import bmr_mifflin_st_jeor


class TestBmrMifflinStJeor:
    def test_male_classic_case(self) -> None:
        # 70 kg, 175 cm, 30 y, male:
        # 10·70 + 6.25·175 - 5·30 + 5 = 700 + 1093.75 - 150 + 5 = 1648.75
        result = bmr_mifflin_st_jeor(weight_kg=70, height_cm=175, age_years=30, sex="male")

        assert result == pytest.approx(1648.75)

    def test_female_classic_case(self) -> None:
        # 60 kg, 165 cm, 28 y, female:
        # 10·60 + 6.25·165 - 5·28 - 161 = 600 + 1031.25 - 140 - 161 = 1330.25
        result = bmr_mifflin_st_jeor(weight_kg=60, height_cm=165, age_years=28, sex="female")

        assert result == pytest.approx(1330.25)


class TestBmrInputValidation:
    """Domain-level guards. API boundary uses Pydantic; this is the inner guard
    so business code can call the function without re-validating."""

    def test_unknown_sex_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="sex"):
            bmr_mifflin_st_jeor(
                weight_kg=70,
                height_cm=175,
                age_years=30,
                sex="Male",  # type: ignore[arg-type]  # intentional runtime probe
            )

    @pytest.mark.parametrize("weight_kg", [0, -1, 29.9, 300.1])
    def test_weight_outside_allowed_range_raises(self, weight_kg: float) -> None:
        with pytest.raises(ValueError, match="weight_kg"):
            bmr_mifflin_st_jeor(weight_kg=weight_kg, height_cm=175, age_years=30, sex="male")

    @pytest.mark.parametrize("height_cm", [0, -10, 99.9, 250.1])
    def test_height_outside_allowed_range_raises(self, height_cm: float) -> None:
        with pytest.raises(ValueError, match="height_cm"):
            bmr_mifflin_st_jeor(weight_kg=70, height_cm=height_cm, age_years=30, sex="male")

    @pytest.mark.parametrize("age_years", [-1, 13, 101])
    def test_age_outside_allowed_range_raises(self, age_years: int) -> None:
        with pytest.raises(ValueError, match="age_years"):
            bmr_mifflin_st_jeor(weight_kg=70, height_cm=175, age_years=age_years, sex="male")
