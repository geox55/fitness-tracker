"""Тесты rule-based интерпретации — REQ-05 + Edge case §10."""

from app.domain.forecast.interpretation import build_interpretation


class TestBuildInterpretation:
    def test_weight_loss_with_fat_loss_explains_fat(self) -> None:
        text = build_interpretation(
            weight_delta_kg=-1.2,
            fat_delta_percent=-1.0,
            muscle_delta_kg=0.1,
            horizon_weeks=4,
            confidence="high",
            fallback=False,
        )

        assert "потеряете" in text
        assert "за счёт жира" in text

    def test_weight_loss_with_muscle_loss_warns(self) -> None:
        text = build_interpretation(
            weight_delta_kg=-1.2,
            fat_delta_percent=0.1,
            muscle_delta_kg=-0.4,
            horizon_weeks=4,
            confidence="high",
            fallback=False,
        )

        assert "за счёт мышц" in text
        assert "пересмотреть" in text

    def test_weight_gain_with_muscle_calls_it_lean(self) -> None:
        text = build_interpretation(
            weight_delta_kg=1.0,
            fat_delta_percent=-0.2,
            muscle_delta_kg=0.6,
            horizon_weeks=4,
            confidence="high",
            fallback=False,
        )

        assert "наберёте" in text
        assert "мышечную массу" in text

    def test_stable_weight_message(self) -> None:
        text = build_interpretation(
            weight_delta_kg=0.05,
            fat_delta_percent=0.0,
            muscle_delta_kg=0.0,
            horizon_weeks=2,
            confidence="medium",
            fallback=False,
        )

        assert "стабильный" in text

    def test_low_confidence_appends_hint(self) -> None:
        text = build_interpretation(
            weight_delta_kg=-0.5,
            fat_delta_percent=-0.3,
            muscle_delta_kg=0.0,
            horizon_weeks=4,
            confidence="low",
            fallback=False,
        )

        assert "точнее" in text
        assert "InBody-измерений" in text

    def test_fallback_appends_note(self) -> None:
        text = build_interpretation(
            weight_delta_kg=-0.5,
            fat_delta_percent=-0.3,
            muscle_delta_kg=0.0,
            horizon_weeks=4,
            confidence="medium",
            fallback=True,
        )

        assert "базовый расчёт" in text

    def test_horizon_pluralization_one_week(self) -> None:
        text = build_interpretation(
            weight_delta_kg=-0.4,
            fat_delta_percent=-0.2,
            muscle_delta_kg=0.0,
            horizon_weeks=1,
            confidence="high",
            fallback=False,
        )

        assert "1 неделю" in text
