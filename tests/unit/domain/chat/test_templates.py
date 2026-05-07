"""Тесты templated-ответов — REQ-11."""

from app.domain.chat.templates import (
    UserContext,
    render_missed_workout,
    render_protein_need,
    render_topic,
    render_what_is_rpe,
    render_why_these_sets,
)


class TestRenderProteinNeed:
    def test_with_full_context_substitutes_grams(self) -> None:
        ctx = UserContext(weight_kg=80.0, goal="muscle_gain", name="Маша")

        result = render_protein_need(ctx)

        assert "80.0 кг" in result.text
        # 80·2.0 = 160 г для muscle_gain
        assert "160" in result.text
        assert result.context["grams"] == 160

    def test_without_context_returns_generic_advice(self) -> None:
        result = render_protein_need(UserContext())

        assert "профиль" in result.text.lower() or "заполните" in result.text.lower()
        assert result.context == {}

    def test_weight_loss_uses_higher_per_kg(self) -> None:
        ctx = UserContext(weight_kg=70.0, goal="weight_loss")

        result = render_protein_need(ctx)

        # 70·1.8 = 126
        assert "126" in result.text


class TestRenderWhatIsRpe:
    def test_static_response(self) -> None:
        result = render_what_is_rpe(UserContext())

        assert "RPE" in result.text
        assert "1" in result.text and "10" in result.text  # шкала
        assert result.context == {}


class TestRenderWhyTheseSets:
    def test_uses_training_level_branch(self) -> None:
        ctx = UserContext(
            training_level="beginner",
            goal="weight_loss",
            name="Аня",
        )

        result = render_why_these_sets(ctx)

        # beginner → 3×10–12
        assert "10" in result.text
        assert "12" in result.text
        assert "Аня" in result.text


class TestRenderMissedWorkout:
    def test_high_frequency_softer_message(self) -> None:
        ctx = UserContext(training_frequency=5)

        result = render_missed_workout(ctx)

        assert "не критичен" in result.text

    def test_low_frequency_recommends_shift(self) -> None:
        ctx = UserContext(training_frequency=3)

        result = render_missed_workout(ctx)

        assert "сдвиньте" in result.text.lower() or "сдвиг" in result.text.lower()


class TestRenderTopicRouter:
    def test_unknown_topic_returns_none(self) -> None:
        assert render_topic("nonexistent_topic", UserContext()) is None

    def test_known_topic_returns_result(self) -> None:
        result = render_topic("what_is_rpe", UserContext())

        assert result is not None
        assert "RPE" in result.text
