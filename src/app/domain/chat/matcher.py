"""Scripted-матчер свободного текста на FAQ-темы — REQ-11.

Простейший подход: lowercased substring match по ключевым словам тем.
Если совпала несколько тем — берём ту, у которой больше совпавших ключей,
при равенстве — первую по порядку TOPICS (стабильность ответов).
"""

from __future__ import annotations

from .topics import TOPICS, Topic


def normalize(text: str) -> str:
    return text.strip().lower()


def match_topic(text: str) -> Topic | None:
    """Найти тему по тексту пользователя; None — не нашли (LLM/fallback)."""
    needle = normalize(text)
    if not needle:
        return None

    best: tuple[int, int, Topic] | None = None  # (score, -priority, topic)
    for priority, topic in enumerate(TOPICS):
        score = sum(1 for kw in topic.keywords if kw in needle)
        if score == 0:
            continue
        candidate = (score, -priority, topic)
        if best is None or candidate > best:
            best = candidate
    return best[2] if best is not None else None
