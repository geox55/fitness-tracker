"""Сервис адаптации плана — spec 009.

В MVP покрываем:
- запись `PlanRebuildEvent` при заметном изменении веса (REQ-01),
- список событий,
- подтверждение пользователем — Scenario 2.2: запускает реальную
  регенерацию плана через `plan.service.generate_plan` (spec 006 §9),
  и только при её успехе помечает событие `user_confirmed` +
  выставляет `applied_at`.

Рекомендация по адаптации показывается баннером в UI; никаких сообщений
пользователю наружу не отправляется.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.adaptation.weight_watcher import (
    WeightDelta,
    compute_delta,
    should_trigger,
)
from ..inbody.models import InBodyMeasurement
from .models import PlanRebuildEvent

if TYPE_CHECKING:
    from ..plan.models import WorkoutPlan


async def _previous_inbody(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    new_inbody: InBodyMeasurement,
) -> InBodyMeasurement | None:
    """Edge case §10: «два InBody подряд за один день — сравниваем с
    предыдущим из другого дня». Берём самый свежий замер старше new.measured_at,
    чей день отличается от дня нового.
    """
    stmt = (
        select(InBodyMeasurement)
        .where(
            InBodyMeasurement.user_id == user_id,
            InBodyMeasurement.id != new_inbody.id,
            InBodyMeasurement.measured_at < new_inbody.measured_at,
            func.date(InBodyMeasurement.measured_at)
            != func.date(new_inbody.measured_at),
        )
        .order_by(desc(InBodyMeasurement.measured_at))
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def maybe_trigger_weight_change(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    new_inbody: InBodyMeasurement,
    now: datetime | None = None,
) -> PlanRebuildEvent | None:
    """REQ-01 + Scenario 1.

    - Если нет предыдущего другого-дневного замера — ничего не делаем
      (пользователь только начал, дельты ещё нет).
    - Если дельта незначительная (Scenario 1.2) — событие не пишем.
    - Если значительная — пишем PlanRebuildEvent(target='workout');
      пользователь увидит баннер «План тренировок устарел» (Scenario 1.1).
    """
    now = now or datetime.now(UTC)
    prev = await _previous_inbody(
        session, user_id=user_id, new_inbody=new_inbody
    )
    if prev is None:
        return None

    delta = compute_delta(
        prev_weight_kg=float(prev.weight_kg),
        new_weight_kg=float(new_inbody.weight_kg),
        prev_measured_at=prev.measured_at,
        new_measured_at=new_inbody.measured_at,
    )
    if not should_trigger(delta):
        return None

    event = await _record_event(
        session,
        user_id=user_id,
        trigger="weight_change",
        target_plan="workout",
        delta=delta,
        now=now,
    )
    return event


async def _record_event(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    trigger: str,
    target_plan: str,
    delta: WeightDelta | None,
    now: datetime,
) -> PlanRebuildEvent:
    event = PlanRebuildEvent(
        user_id=user_id,
        trigger=trigger,
        target_plan=target_plan,
        status="pending",
        delta_kg=(
            Decimal(str(round(delta.delta_kg, 2))) if delta is not None else None
        ),
        delta_percent=(
            Decimal(str(round(delta.delta_percent, 2)))
            if delta is not None
            else None
        ),
        triggered_at=now,
    )
    session.add(event)
    await session.flush()
    return event


# ---------------------------------------------------------------------------
# Чтение и подтверждение пользователем
# ---------------------------------------------------------------------------


async def list_events(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    status_filter: str | None,
    limit: int,
    offset: int,
) -> tuple[list[PlanRebuildEvent], int]:
    base = select(PlanRebuildEvent).where(PlanRebuildEvent.user_id == user_id)
    count_base = select(func.count(PlanRebuildEvent.id)).where(
        PlanRebuildEvent.user_id == user_id
    )
    if status_filter is not None:
        base = base.where(PlanRebuildEvent.status == status_filter)
        count_base = count_base.where(PlanRebuildEvent.status == status_filter)
    items_stmt = (
        base.order_by(PlanRebuildEvent.triggered_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = list((await session.execute(items_stmt)).scalars().all())
    total = (await session.execute(count_base)).scalar_one()
    return items, int(total)


async def confirm_rebuild(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    target: str,
    now: datetime | None = None,
) -> tuple[PlanRebuildEvent, WorkoutPlan, list[str]]:
    """Scenario 2.2: пользователь нажал CTA «Обновить».

    Поток:
    1. Берём последнее pending-событие на этот target (или создаём
       manual-pending — пользователь нажал «Обновить» при чистом списке).
    2. Запускаем `generate_plan` — он сам архивирует прошлый active и
       создаёт новый (spec 006 §9 REQ-13).
    3. Только при успехе генерации помечаем событие `user_confirmed`
       и проставляем `applied_at` — иначе аудит будет врать.

    Если `generate_plan` бросает `PreconditionsNotMet`, мы прокидываем
    исключение наружу: событие остаётся pending, пользователю покажется
    та же 400-ошибка, что и при ручной генерации через `/plans/generate`.
    """
    # Импорт здесь, а не наверху, чтобы избежать циклической зависимости
    # adaptation ↔ plan (plan не зависит от adaptation, но импортить
    # симметрично надёжнее).
    from ..plan.service import generate_plan

    now = now or datetime.now(UTC)
    stmt = (
        select(PlanRebuildEvent)
        .where(
            PlanRebuildEvent.user_id == user_id,
            PlanRebuildEvent.status == "pending",
            PlanRebuildEvent.target_plan == target,
        )
        .order_by(PlanRebuildEvent.triggered_at.desc())
        .limit(1)
    )
    event = (await session.execute(stmt)).scalar_one_or_none()
    if event is None:
        event = PlanRebuildEvent(
            user_id=user_id,
            trigger="manual",
            target_plan=target,
            status="pending",
            triggered_at=now,
        )
        session.add(event)
        await session.flush()

    # PreconditionsNotMet прокидываем — event остаётся pending.
    plan, warnings = await generate_plan(session, user_id=user_id, now=now)

    event.status = "user_confirmed"
    event.applied_at = now
    await session.flush()
    return event, plan, warnings
