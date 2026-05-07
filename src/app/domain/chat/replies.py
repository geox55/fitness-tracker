"""Координатор ответа ассистента — собирает scripted/templated/llm-ветки.

Чистая функция: на вход текст пользователя + контекст + флаги,
на выход — `AssistantReply` (что отвечать и какой `source`). LLM здесь
**не вызывается** — для этого нужно сетевое I/O; service.py вместо неё
зовёт коллабораторов и потом записывает результат в БД.

Ради тестируемости разделили: `decide_reply` отвечает за выбор ветки,
`compose_llm_disclaimer` — за обязательный хвост LLM-ответа (REQ-15).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .matcher import match_topic
from .sensitive import DISCLAIMER_TEXT, is_sensitive
from .templates import RENDERERS, UserContext, render_topic

ReplyKind = Literal["scripted", "templated", "llm", "fallback", "sensitive"]


@dataclass(frozen=True)
class AssistantReply:
    text: str
    source: str  # 'scripted' | 'templated' | 'llm' | 'fallback'
    kind: ReplyKind  # внутренняя категория для логов / LLM-trigger
    context: dict[str, object]


# Используется, когда LLM выключен и scripted не нашёл темы (Scenario 6.2).
DEFAULT_FALLBACK_TEXT = (
    "Я пока не умею отвечать на это. Попробуйте перефразировать или "
    "выберите тему ниже."
)


LLM_DISCLAIMER_SUFFIX = "\n\nЭто персональный совет, не медицинская рекомендация."


def decide_reply(
    *,
    user_text: str,
    user_context: UserContext,
    topic_id: str | None = None,
    llm_enabled: bool,
) -> AssistantReply:
    """Главный «маршрутизатор» ответа.

    Порядок проверок:
    1. Sensitive: всегда выигрывает — REQ-13.
    2. Topic_id (явный quick-reply) → templated.
    3. Совпадение по ключевым словам → templated.
    4. LLM включён → kind='llm' (вызов делает service.py).
    5. Иначе → fallback (Scenario 6.2).
    """
    if is_sensitive(user_text):
        return AssistantReply(
            text=DISCLAIMER_TEXT,
            source="scripted",
            kind="sensitive",
            context={},
        )

    if topic_id is not None and topic_id in RENDERERS:
        rendered = render_topic(topic_id, user_context)
        if rendered is not None:
            return AssistantReply(
                text=rendered.text,
                source="templated",
                kind="templated",
                context=rendered.context,
            )

    matched = match_topic(user_text)
    if matched is not None:
        rendered = render_topic(matched.id, user_context)
        if rendered is not None:
            return AssistantReply(
                text=rendered.text,
                source="templated",
                kind="templated",
                context={"topic_id": matched.id, **rendered.context},
            )

    if llm_enabled:
        # Маркер для service.py: вызови LLM, и при успехе подмени text.
        return AssistantReply(
            text="",
            source="llm",
            kind="llm",
            context={},
        )

    return AssistantReply(
        text=DEFAULT_FALLBACK_TEXT,
        source="scripted",
        kind="fallback",
        context={},
    )


def attach_llm_disclaimer(text: str) -> str:
    """REQ-15: всегда добавляем дисклеймер к LLM-ответу."""
    text = text.rstrip()
    if not text:
        return text
    if "не медицинская рекомендация" in text:
        return text
    return text + LLM_DISCLAIMER_SUFFIX
