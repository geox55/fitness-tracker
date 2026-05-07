"""Каталог тем чата (FAQ) — REQ-10/11.

`Topic` описывает одну сценарную тему: id, кнопка-quick-reply, ключевые слова
для матчера, и template_kind — статичный текст или templated с подстановкой.

Сами тексты рендерятся в `templates.py` (чтобы здесь не смешивать справочник
тем и логику подстановки).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    id: str
    quick_reply: str  # надпись на чипе
    keywords: tuple[str, ...]  # для scripted-матчера


# Список зафиксирован — менять только осознанно. UI порядок = порядок здесь.
TOPICS: tuple[Topic, ...] = (
    Topic(
        id="why_these_sets",
        quick_reply="Почему мне дали такие подходы?",
        keywords=("почему", "подход", "сет", "повтор"),
    ),
    Topic(
        id="what_is_rpe",
        quick_reply="Что такое RPE?",
        keywords=("rpe", "рпэ", "сложность"),
    ),
    Topic(
        id="protein_need",
        quick_reply="Зачем мне белок?",
        keywords=("белок", "протеин", "белки"),
    ),
    Topic(
        id="pre_workout_food",
        quick_reply="Что съесть до тренировки?",
        keywords=("до тренировки", "перед тренировкой", "до зала"),
    ),
    Topic(
        id="missed_workout",
        quick_reply="Я пропустил тренировку, что делать?",
        keywords=("пропустил", "не пошёл", "не пошел", "не успел"),
    ),
    Topic(
        id="rest_days",
        quick_reply="Сколько отдыхать между тренировками?",
        keywords=("отдых", "отдыхать", "восстановление"),
    ),
    Topic(
        id="weight_plateau",
        quick_reply="Вес встал — что делать?",
        keywords=("вес встал", "плато", "не худею", "не растёт"),
    ),
)


def find_topic_by_id(topic_id: str) -> Topic | None:
    for t in TOPICS:
        if t.id == topic_id:
            return t
    return None


def quick_reply_ids() -> list[str]:
    return [t.id for t in TOPICS]
