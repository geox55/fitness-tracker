"""Сервис адаптации плана — spec 009.

В MVP покрываем:
- запись `PlanRebuildEvent` при заметном изменении веса (REQ-01),
- запись `PlanRebuildEvent` при смене goal/training_frequency в профиле
  (REQ-02),
- фоновую проверку конца 4-недельного цикла и принудительной перегенерации
  через 7 дней игнора баннера (REQ-03 + REQ-04),
- список событий,
- подтверждение пользователем — Scenario 2.2: запускает реальную
  регенерацию плана через `plan.service.generate_plan` (spec 006 §9),
  и только при её успехе помечает событие `user_confirmed` +
  выставляет `applied_at`.

Рекомендация по адаптации показывается баннером в UI; никаких сообщений
пользователю наружу не отправляется.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.adaptation.weight_watcher import (
    WeightDelta,
    compute_delta,
    should_trigger,
)
from ..inbody.models import InBodyMeasurement
from ..plan.models import WorkoutPlan
from ..plan.service import (
    ActivePlanRaceError,
    PreconditionsNotMet,
    generate_plan,
)
from .models import PlanRebuildEvent

_log = logging.getLogger(__name__)

# REQ-04: сколько дней баннер «План устарел» может висеть без реакции
# пользователя до принудительной регенерации.
FORCE_REBUILD_AFTER_DAYS = 7


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


# Какому полю профиля какой trigger соответствует (REQ-02). Поле
# `equipment_available` сюда не входит: в enum нет подходящего значения,
# поэтому смена оборудования отражается только флагом `plan_rebuild_required`.
_PROFILE_FIELD_TO_TRIGGER: dict[str, str] = {
    "goal": "goal_change",
    "training_frequency": "frequency_change",
}


async def record_profile_change_events(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    changed_fields: set[str],
    now: datetime | None = None,
) -> list[PlanRebuildEvent]:
    """REQ-02 + Scenario 2: на смену goal/training_frequency создаём
    PlanRebuildEvent. Edge case §10: debounce — если pending-событие с тем
    же триггером уже есть, не дублируем (изменение поля несколько раз за
    день должно ставить флаг один раз, не запускать регенерацию заново).
    """
    now = now or datetime.now(UTC)
    created: list[PlanRebuildEvent] = []
    for field in changed_fields:
        trigger = _PROFILE_FIELD_TO_TRIGGER.get(field)
        if trigger is None:
            # equipment_available и т.п. — без отдельного триггера.
            continue
        if await _has_pending(session, user_id=user_id, trigger=trigger):
            continue
        event = await _record_event(
            session,
            user_id=user_id,
            trigger=trigger,
            target_plan="workout",
            delta=None,
            now=now,
        )
        created.append(event)
    return created


async def _has_pending(
    session: AsyncSession, *, user_id: uuid.UUID, trigger: str
) -> bool:
    stmt = select(PlanRebuildEvent.id).where(
        PlanRebuildEvent.user_id == user_id,
        PlanRebuildEvent.trigger == trigger,
        PlanRebuildEvent.status == "pending",
    ).limit(1)
    return (await session.execute(stmt)).scalar_one_or_none() is not None


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


@dataclass(frozen=True)
class BackgroundCheckReport:
    """Сводка для cron-ответа: сколько пользователей обработано и почему."""

    cycle_end_rebuilt: int
    force_rebuilt: int
    skipped: int


async def run_background_check(
    session: AsyncSession,
    *,
    now: datetime | None = None,
    force_after_days: int = FORCE_REBUILD_AFTER_DAYS,
) -> BackgroundCheckReport:
    """REQ-03 + REQ-04: проходит по всем пользователям и автоматически
    регенерирует план там, где:

    - активный план просрочен (`valid_until <= today`) — Scenario 3;
    - есть pending-событие старше `force_after_days` — Scenario 2.3.

    Каждый пользователь обрабатывается в своём savepoint: если у одного
    профиль не дотягивает до preconditions — продолжаем со следующим, а не
    валим всю пачку. Pending-события успешного пользователя помечаются
    `auto_applied`, событий cycle_end до этого может не быть (Scenario 3
    срабатывает без UI), поэтому создаём его ретроактивно — для аудита.
    """
    now = now or datetime.now(UTC)
    today = now.date()
    force_threshold = now - timedelta(days=force_after_days)

    cycle_user_ids = set(
        (
            await session.execute(
                select(WorkoutPlan.user_id).where(
                    WorkoutPlan.status == "active",
                    WorkoutPlan.valid_until <= today,
                )
            )
        ).scalars().all()
    )
    force_user_ids = set(
        (
            await session.execute(
                select(PlanRebuildEvent.user_id)
                .where(
                    PlanRebuildEvent.status == "pending",
                    PlanRebuildEvent.triggered_at <= force_threshold,
                )
                .distinct()
            )
        ).scalars().all()
    )

    cycle_end_count = 0
    force_count = 0
    skipped = 0
    # Объединяем, чтобы у пользователя, попавшего в обе категории, не было
    # двух регенераций.
    for user_id in cycle_user_ids | force_user_ids:
        is_cycle = user_id in cycle_user_ids
        is_force = user_id in force_user_ids
        try:
            await _rebuild_for_user(
                session,
                user_id=user_id,
                now=now,
                is_cycle_end=is_cycle,
            )
        except PreconditionsNotMet as exc:
            _log.warning(
                "adaptation: user %s skipped (preconditions: %s)",
                user_id, exc.missing,
            )
            skipped += 1
            continue
        except ActivePlanRaceError:
            # generate_plan уже сделал session.rollback() — внутренний
            # savepoint потерян, дальше итерироваться нельзя безопасно.
            _log.warning("adaptation: race on user %s, aborting batch", user_id)
            skipped += 1
            break

        if is_cycle:
            cycle_end_count += 1
        if is_force:
            force_count += 1

    return BackgroundCheckReport(
        cycle_end_rebuilt=cycle_end_count,
        force_rebuilt=force_count,
        skipped=skipped,
    )


async def _rebuild_for_user(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    now: datetime,
    is_cycle_end: bool,
) -> None:
    """Регенерация плана для одного пользователя + проставление событий.

    Если событие cycle_end ещё не создавалось (Scenario 3 — баннера нет,
    флага в БД тоже нет), создаём его ретроактивно со статусом
    `auto_applied`. Все остальные pending-события того же пользователя
    тоже закрываем — пользователь получит свежий план и старый аудит
    больше не актуален.
    """
    _plan, _warnings = await generate_plan(session, user_id=user_id, now=now)

    pending_stmt = select(PlanRebuildEvent).where(
        PlanRebuildEvent.user_id == user_id,
        PlanRebuildEvent.status == "pending",
    )
    pending = list((await session.execute(pending_stmt)).scalars().all())
    has_cycle_event = any(ev.trigger == "cycle_end" for ev in pending)
    for ev in pending:
        ev.status = "auto_applied"
        ev.applied_at = now

    if is_cycle_end and not has_cycle_event:
        session.add(
            PlanRebuildEvent(
                user_id=user_id,
                trigger="cycle_end",
                target_plan="workout",
                status="auto_applied",
                triggered_at=now,
                applied_at=now,
            )
        )
    await session.flush()


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

    # Если generate_plan бросит — event ещё не помечен confirmed, и rollback
    # в обвязке снесёт и его (для manual-варианта он даже не успел во flush).
    plan, warnings = await generate_plan(session, user_id=user_id, now=now)

    event.status = "user_confirmed"
    event.applied_at = now
    await session.flush()
    return event, plan, warnings
