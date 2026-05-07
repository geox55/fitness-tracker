"""Adaptation endpoints — spec 009 §9."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query, status

from ...domains.adaptation.schemas import (
    PlanRebuildEventList,
    PlanRebuildEventRead,
    RebuildPlanRequest,
    RebuildPlanResponse,
)
from ...domains.adaptation.service import confirm_rebuild, list_events
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(tags=["adaptation"])


@router.get(
    "/adaptation/events", response_model=PlanRebuildEventList
)
async def get_events(
    user: CurrentUserDep,
    session: SessionDep,
    status_filter: Literal[
        "pending", "auto_applied", "user_confirmed", "dismissed"
    ]
    | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PlanRebuildEventList:
    items, total = await list_events(
        session,
        user_id=user.id,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )
    return PlanRebuildEventList(
        items=[PlanRebuildEventRead.model_validate(e) for e in items],
        total=total,
    )


@router.post(
    "/plans/rebuild",
    response_model=RebuildPlanResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def post_rebuild(
    payload: RebuildPlanRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> RebuildPlanResponse:
    """Scenario 2.2 — пользователь подтверждает регенерацию.

    Возвращаем 202: реальная генерация плана идёт в specs 006/007 и
    подключится отдельной задачей. Сейчас фиксируем намерение и переводим
    событие в `user_confirmed`.
    """
    event = await confirm_rebuild(
        session, user_id=user.id, target=payload.target
    )
    return RebuildPlanResponse(
        event_id=event.id,
        target_plan=event.target_plan,
        status=event.status,
        detail=(
            "Регенерация плана будет запущена. "
            "ML-генератор подключится после завершения spec 006/007."
        ),
    )
