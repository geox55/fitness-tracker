"""Тесты scripted-матчера — REQ-11."""

from app.domain.chat.matcher import match_topic


class TestMatchTopic:
    def test_exact_keyword_match(self) -> None:
        topic = match_topic("что такое RPE?")

        assert topic is not None
        assert topic.id == "what_is_rpe"

    def test_phrase_with_extra_words(self) -> None:
        topic = match_topic("Я пропустил тренировку, что делать?")

        assert topic is not None
        assert topic.id == "missed_workout"

    def test_case_insensitive(self) -> None:
        topic = match_topic("ЗАЧЕМ МНЕ БЕЛОК")

        assert topic is not None
        assert topic.id == "protein_need"

    def test_no_match_returns_none(self) -> None:
        assert match_topic("случайный текст про погоду") is None

    def test_empty_returns_none(self) -> None:
        assert match_topic("") is None
        assert match_topic("   ") is None

    def test_higher_score_wins(self) -> None:
        # У темы missed_workout два явных ключа («пропустил» + «не успел»),
        # у других — по одному; матчер выбирает её.
        topic = match_topic("я пропустил и не успел дойти до зала")

        assert topic is not None
        assert topic.id == "missed_workout"

    def test_tie_breaks_by_topics_order(self) -> None:
        # Гарантируем стабильность: если два совпадения с одинаковым счётом,
        # побеждает первая по порядку TOPICS.
        # «отдых» — keyword у rest_days; «вес встал» — у weight_plateau.
        topic = match_topic("отдых и вес встал")

        assert topic is not None
        # rest_days идёт раньше weight_plateau в TOPICS — она и выигрывает
        # при равенстве. Регрессия в обратную сторону ломает порядок UI.
        assert topic.id == "rest_days"
