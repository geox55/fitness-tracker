_ACTIVITY_MULTIPLIER: dict[int, float] = {
    2: 1.375,
    3: 1.55,
    4: 1.55,
    5: 1.725,
    6: 1.725,
}


def tdee(bmr_kcal: float, training_frequency: int) -> float:
    if training_frequency not in _ACTIVITY_MULTIPLIER:
        allowed = sorted(_ACTIVITY_MULTIPLIER)
        raise ValueError(
            f"training_frequency must be in {allowed}, got {training_frequency}"
        )
    return bmr_kcal * _ACTIVITY_MULTIPLIER[training_frequency]
