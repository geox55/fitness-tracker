"""Тесты координатора ответа decide_reply — Scenarios 5, 6.1, 6.2, 6.3."""

from app.domain.chat.replies import (
    DEFAULT_FALLBACK_TEXT,
    LLM_DISCLAIMER_SUFFIX,
    attach_llm_disclaimer,
    decide_reply,
)
from app.domain.chat.sensitive import DISCLAIMER_TEXT
from app.domain.chat.templates import UserContext


class TestDecideReply:
    def test_sensitive_wins_over_topic_id(self) -> None:
        # Если пользователь нажал quick-reply, но в content есть «болит» —
        # всё равно отдаём дисклеймер. Это требование REQ-13.
        reply = decide_reply(
            user_text="у меня болит колено",
            user_context=UserContext(),
            topic_id="what_is_rpe",
            llm_enabled=True,
        )

        assert reply.kind == "sensitive"
        assert reply.text == DISCLAIMER_TEXT

    def test_explicit_topic_id_uses_template(self) -> None:
        reply = decide_reply(
            user_text="что-то совсем другое",
            user_context=UserContext(),
            topic_id="what_is_rpe",
            llm_enabled=False,
        )

        assert reply.kind == "templated"
        assert "RPE" in reply.text

    def test_keyword_match_uses_template(self) -> None:
        reply = decide_reply(
            user_text="зачем мне белок?",
            user_context=UserContext(weight_kg=70.0, goal="muscle_gain"),
            topic_id=None,
            llm_enabled=False,
        )

        assert reply.kind == "templated"
        assert reply.context.get("topic_id") == "protein_need"

    def test_no_match_with_llm_returns_llm_marker(self) -> None:
        reply = decide_reply(
            user_text="можно ли есть мороженое после тренировки в полнолуние?",
            user_context=UserContext(),
            topic_id=None,
            llm_enabled=True,
        )

        assert reply.kind == "llm"
        # Текст пуст: его подставит service.py после реального LLM-вызова.
        assert reply.text == ""

    def test_no_match_without_llm_returns_default_fallback(self) -> None:
        reply = decide_reply(
            user_text="случайный вопрос про погоду",
            user_context=UserContext(),
            topic_id=None,
            llm_enabled=False,
        )

        assert reply.kind == "fallback"
        assert reply.text == DEFAULT_FALLBACK_TEXT


class TestAttachLlmDisclaimer:
    def test_appends_disclaimer(self) -> None:
        text = attach_llm_disclaimer("Можно, но в умеренных количествах.")

        assert text.endswith(LLM_DISCLAIMER_SUFFIX)
        assert "не медицинская рекомендация" in text

    def test_idempotent_when_already_present(self) -> None:
        original = "Совет.\n\nЭто персональный совет, не медицинская рекомендация."
        result = attach_llm_disclaimer(original)

        # Не должно быть дублирования.
        assert result.count("не медицинская рекомендация") == 1

    def test_empty_returns_empty(self) -> None:
        assert attach_llm_disclaimer("") == ""
