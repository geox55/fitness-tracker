"""Сервис уведомлений: enqueue с debounce, поиск кандидатов на inbody-reminder.

Чистые helpers (`should_send`, `_inbody_reminder_due`) тестируются без БД.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.models import User
from ..inbody.models import InBodyMeasurement
from .models import (
    USER_CONTROLLED_TYPES,
    NotificationOutbox,
    NotificationPreferences,
    NotificationType,
)

# spec 011 REQ-05: повторно >30 дней; debounce 7 дней.
INBODY_REMINDER_AFTER_DAYS = 30
INBODY_REMINDER_DEBOUNCE_DAYS = 7


def _is_type_enabled(prefs: NotificationPreferences | None, kind: str) -> bool:
    """Auth-typeы (email_verify/password_reset) идут всегда; пользовательские
    уважают тоглы. Если preferences ещё не созданы — считаем дефолты (все True).
    """
    if kind not in USER_CONTROLLED_TYPES:
        return True
    if prefs is None:
        return True  # дефолты в модели — True
    return bool(getattr(prefs, kind))


def _is_channel_enabled(
    prefs: NotificationPreferences | None, channel: str
) -> bool:
    if channel == "in_app":
        return True
    if prefs is None:
        return True
    return prefs.email_enabled


def should_send(
    *,
    prefs: NotificationPreferences | None,
    kind: str,
    channel: str,
) -> bool:
    """Чистая комбинация: settings × channel.

    Auth-типы (email_verify/password_reset) идут всегда — они нужны для самой
    возможности пользоваться аккаунтом; пользовательский тогл "email_enabled"
    их не блокирует.
    """
    if kind not in USER_CONTROLLED_TYPES:
        return True
    return _is_type_enabled(prefs, kind) and _is_channel_enabled(prefs, channel)


async def get_or_create_preferences(
    session: AsyncSession, *, user_id: uuid.UUID
) -> NotificationPreferences:
    prefs = await session.get(NotificationPreferences, user_id)
    if prefs is None:
        prefs = NotificationPreferences(user_id=user_id)
        session.add(prefs)
        await session.flush()
    return prefs


async def update_preferences(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    changes: dict[str, bool],
) -> NotificationPreferences:
    prefs = await get_or_create_preferences(session, user_id=user_id)
    for k, v in changes.items():
        setattr(prefs, k, v)
    await session.flush()
    return prefs


async def _was_sent_in_window(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    kind: str,
    channel: str,
    window: timedelta,
    now: datetime,
) -> bool:
    """Debounce check (REQ-12): был ли такой же type+channel в окне."""
    threshold = now - window
    stmt = (
        select(func.count(NotificationOutbox.id))
        .where(
            NotificationOutbox.user_id == user_id,
            NotificationOutbox.type == kind,
            NotificationOutbox.channel == channel,
            NotificationOutbox.created_at >= threshold,
            NotificationOutbox.status != "failed",
        )
    )
    return ((await session.execute(stmt)).scalar_one() or 0) > 0


async def enqueue(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    kind: NotificationType,
    channel: str,
    context_key: str,
    payload: dict[str, Any] | None = None,
    debounce: timedelta | None = None,
    now: datetime | None = None,
) -> NotificationOutbox | None:
    """Добавить уведомление в outbox. Возвращает None, если:
    - тип/канал отключён в preferences;
    - debounce-окно не прошло.

    in-app сразу помечается status='sent', sent_at=now (доставка == создание
    записи). email — status='queued', реальная отправка идёт отдельным воркером.
    """
    now = now or datetime.now(UTC)

    prefs = await session.get(NotificationPreferences, user_id)
    if not should_send(prefs=prefs, kind=kind, channel=channel):
        return None

    if debounce is not None and await _was_sent_in_window(
        session,
        user_id=user_id,
        kind=kind,
        channel=channel,
        window=debounce,
        now=now,
    ):
        return None

    item = NotificationOutbox(
        user_id=user_id,
        type=kind,
        channel=channel,
        context_key=context_key,
        payload=payload or {},
        status="sent" if channel == "in_app" else "queued",
        sent_at=now if channel == "in_app" else None,
    )
    session.add(item)
    await session.flush()
    return item


# ---- Inbox -----------------------------------------------------------------


async def list_inbox(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    unread_only: bool,
    limit: int,
    offset: int,
) -> tuple[list[NotificationOutbox], int, int]:
    """Возвращает (items, unread_count, total). unread_count считается всегда
    по всему inbox, не по странице — для бейджа в UI."""
    base = select(NotificationOutbox).where(
        NotificationOutbox.user_id == user_id,
        NotificationOutbox.channel == "in_app",
    )
    items_stmt = base
    if unread_only:
        items_stmt = items_stmt.where(NotificationOutbox.read_at.is_(None))
    items_stmt = (
        items_stmt
        # Непрочитанные сверху (Scenario 7), затем по дате DESC.
        .order_by(
            NotificationOutbox.read_at.is_(None).desc(),
            NotificationOutbox.created_at.desc(),
        )
        .offset(offset)
        .limit(limit)
    )
    items = list((await session.execute(items_stmt)).scalars().all())

    total_stmt = select(func.count(NotificationOutbox.id)).where(
        NotificationOutbox.user_id == user_id,
        NotificationOutbox.channel == "in_app",
    )
    total = (await session.execute(total_stmt)).scalar_one()
    unread = (
        await session.execute(
            total_stmt.where(NotificationOutbox.read_at.is_(None))
        )
    ).scalar_one()
    return items, int(unread), int(total)


async def mark_read(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    notification_id: uuid.UUID,
    now: datetime | None = None,
) -> NotificationOutbox | None:
    item = await session.get(NotificationOutbox, notification_id)
    if (
        item is None
        or item.user_id != user_id
        or item.channel != "in_app"
    ):
        return None
    if item.read_at is None:
        item.read_at = now or datetime.now(UTC)
    return item


async def delete_notification(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    notification_id: uuid.UUID,
) -> bool:
    item = await session.get(NotificationOutbox, notification_id)
    if item is None or item.user_id != user_id:
        return False
    await session.delete(item)
    return True


# ---- Кандидат для cron-job: "пора напомнить про InBody" --------------------


def _inbody_reminder_due(
    *, last_measured_at: datetime | None, now: datetime
) -> bool:
    """Прошло ≥30 дней с последнего измерения (или их вообще не было).

    Если измерений нет — напоминание тоже валидно: пользователь зарегистрирован,
    но ещё ни разу не вводил данные. caller дополнительно отрежет тех, кто
    онбординг не закончил.
    """
    if last_measured_at is None:
        return True
    elapsed = now - last_measured_at
    return elapsed >= timedelta(days=INBODY_REMINDER_AFTER_DAYS)


async def find_inbody_reminder_candidates(
    session: AsyncSession, *, now: datetime | None = None
) -> list[uuid.UUID]:
    """Список user_id, у которых пора напомнить про InBody. Без debounce —
    его проверит enqueue() при отправке.

    Логика:
    - выбираем active-пользователей (email подтверждён, не удалён);
    - JOIN с last_measured_at; LEFT JOIN, чтобы поймать "ни одного измерения";
    - фильтруем тех, у кого прошло ≥30 дней или нет измерений вовсе.
    """
    now = now or datetime.now(UTC)
    threshold = now - timedelta(days=INBODY_REMINDER_AFTER_DAYS)
    last_at = (
        select(
            InBodyMeasurement.user_id.label("uid"),
            func.max(InBodyMeasurement.measured_at).label("last_at"),
        )
        .group_by(InBodyMeasurement.user_id)
        .subquery()
    )
    stmt = (
        select(User.id)
        .outerjoin(last_at, last_at.c.uid == User.id)
        .where(
            User.deleted_at.is_(None),
            User.email_status == "active",
            (last_at.c.last_at.is_(None)) | (last_at.c.last_at < threshold),
        )
    )
    rows = (await session.execute(stmt)).scalars().all()
    return list(rows)
