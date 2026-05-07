"""Тесты детектора чувствительных тем — REQ-13."""

import pytest

from app.domain.chat.sensitive import is_sensitive


class TestIsSensitive:
    @pytest.mark.parametrize(
        "text",
        [
            "у меня болит спина",
            "была травма колена",
            "прыгает давление",
            "что мне принимать таблетки",
            "не хочу жить",
            "у меня депрессия",
        ],
    )
    def test_flags_sensitive_phrases(self, text: str) -> None:
        assert is_sensitive(text)

    @pytest.mark.parametrize(
        "text",
        [
            "сколько белка съесть",
            "что такое RPE?",
            "как считать тоннаж",
            "вес встал, что делать",
        ],
    )
    def test_does_not_flag_normal_questions(self, text: str) -> None:
        assert not is_sensitive(text)

    def test_empty_text_not_sensitive(self) -> None:
        assert not is_sensitive("")
        assert not is_sensitive("   ")
