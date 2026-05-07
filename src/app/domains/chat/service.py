"""Чат-сервис — БД-обвязка для spec 009 §9.

LLM-вызов вынесен в коллаборатор `LLMClient` (Protocol). По умолчанию
сервис работает без LLM — REQ-12: feature-flag через `chat_llm_enabled`.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.chat.rate_limit import ChatRateLimiter, get_chat_limiter
from ...domain.chat.replies import (
    AssistantReply,
    attach_llm_disclaimer,
    decide_reply,
)
from ...domain.chat.templates import UserContext
from ..profile.models import UserProfile
from .models import ChatMessage

_log = logging.getLogger("app.chat")


class ChatError(Exception):
    code: str = "chat_error"


class RateLimitedError(ChatError):
    code = "rate_limited"


class LLMUnavailableError(ChatError):
    """LLM включён, но что-то пошло не так — сервис вернёт 503."""

    code = "llm_unavailable"


class LLMClient(Protocol):
    async def generate(
        self, *, prompt: str, context: dict[str, object]
    ) -> str: ...  # pragma: no cover — Protocol


# ---------------------------------------------------------------------------


async def _load_user_context(
    session: AsyncSession, user_id: uuid.UUID
) -> UserContext:
    """Срез профиля для шаблонов. Если профиля нет — пустой контекст."""
    profile = await session.get(UserProfile, user_id)
    if profile is None:
        return UserContext()
    return UserContext(
        name=profile.name,
        goal=profile.goal,
        training_level=profile.training_level,
        training_frequency=profile.training_frequency,
        weight_kg=(
            float(profile.baseline_weight_kg)
            if profile.baseline_weight_kg is not None
            else None
        ),
        bmr_kcal=profile.bmr_kcal,
    )


async def list_messages(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    limit: int,
    before: datetime | None,
) -> tuple[list[ChatMessage], int]:
    base = select(ChatMessage).where(ChatMessage.user_id == user_id)
    if before is not None:
        base = base.where(ChatMessage.created_at < before)
    items_stmt = base.order_by(ChatMessage.created_at.desc()).limit(limit)
    items = list((await session.execute(items_stmt)).scalars().all())
    total = (
        await session.execute(
            select(func.count(ChatMessage.id)).where(ChatMessage.user_id == user_id)
        )
    ).scalar_one()
    return items, int(total)


async def post_message(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    content: str,
    topic_id: str | None,
    llm_enabled: bool,
    llm: LLMClient | None = None,
    limiter: ChatRateLimiter | None = None,
    now: datetime | None = None,
) -> tuple[ChatMessage, ChatMessage]:
    """Сохранить сообщение пользователя и сгенерировать ответ ассистента.

    Порядок:
    1. Rate-limit (Edge case §10).
    2. decide_reply → ветка ответа.
    3. Если ветка == 'llm' и llm-клиент передан — вызвать; при ошибке упасть
       с LLMUnavailableError, чтобы API ответил 503 (REQ-12, Scenario 6.2).
    4. Записать обе записи в одной транзакции.
    """
    now = now or datetime.now(UTC)
    limiter = limiter or get_chat_limiter()
    if not limiter.is_allowed(user_id, now):
        raise RateLimitedError("chat rate limit exceeded")

    user_ctx = await _load_user_context(session, user_id)
    decision = decide_reply(
        user_text=content,
        user_context=user_ctx,
        topic_id=topic_id,
        llm_enabled=llm_enabled,
    )

    final = await _materialize_llm_if_needed(
        decision, content=content, llm=llm, llm_enabled=llm_enabled
    )

    user_msg = ChatMessage(
        user_id=user_id,
        author="user",
        content=content,
        source="user",
        context={"topic_id": topic_id} if topic_id else {},
        created_at=now,
    )
    assistant_msg = ChatMessage(
        user_id=user_id,
        author="assistant",
        content=final.text,
        source=final.source,
        context=dict(final.context),
        created_at=now,
    )
    session.add_all([user_msg, assistant_msg])
    await session.flush()

    limiter.record(user_id, now)
    return user_msg, assistant_msg


async def _materialize_llm_if_needed(
    decision: AssistantReply,
    *,
    content: str,
    llm: LLMClient | None,
    llm_enabled: bool,
) -> AssistantReply:
    if decision.kind != "llm":
        return decision

    if not llm_enabled or llm is None:
        # Сюда мы попадаем, если decide_reply вернула llm-ветку (значит флаг
        # был True), но конкретный клиент не передан — это конфигурационная
        # ошибка. По спеке Scenario 6.2 — отвечаем дефолтным fallback'ом.
        _log.warning("llm requested but client not configured")
        from ...domain.chat.replies import DEFAULT_FALLBACK_TEXT

        return AssistantReply(
            text=DEFAULT_FALLBACK_TEXT,
            source="scripted",
            kind="fallback",
            context={},
        )

    try:
        text = await llm.generate(prompt=content, context={})
    except Exception as exc:
        _log.exception("llm call failed")
        raise LLMUnavailableError("llm provider failed") from exc

    return AssistantReply(
        text=attach_llm_disclaimer(text),
        source="llm",
        kind="llm",
        context={"llm": True},
    )
