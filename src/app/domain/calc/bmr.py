from typing import Literal

Sex = Literal["male", "female"]

_MALE_OFFSET = 5
_FEMALE_OFFSET = -161

# Profile-level ranges (spec 002). Out-of-range inputs are usage errors,
# not user errors — Pydantic validates at the API boundary.
_WEIGHT_MIN, _WEIGHT_MAX = 30.0, 300.0
_HEIGHT_MIN, _HEIGHT_MAX = 100.0, 250.0
_AGE_MIN, _AGE_MAX = 14, 100


def _check_range(name: str, value: float, low: float, high: float) -> None:
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def bmr_mifflin_st_jeor(
    weight_kg: float,
    height_cm: float,
    age_years: int,
    sex: Sex,
) -> float:
    if sex not in ("male", "female"):
        raise ValueError(f"sex must be 'male' or 'female', got {sex!r}")
    _check_range("weight_kg", weight_kg, _WEIGHT_MIN, _WEIGHT_MAX)
    _check_range("height_cm", height_cm, _HEIGHT_MIN, _HEIGHT_MAX)
    _check_range("age_years", age_years, _AGE_MIN, _AGE_MAX)

    sex_offset = _MALE_OFFSET if sex == "male" else _FEMALE_OFFSET
    return 10 * weight_kg + 6.25 * height_cm - 5 * age_years + sex_offset
