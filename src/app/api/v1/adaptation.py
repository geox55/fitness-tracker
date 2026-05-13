"""Adaptation endpoints — spec 009 §9."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from ...domains.adaptation.schemas import (
    PlanRebuildEventList,
    PlanRebuildEventRead,
    RebuildPlanRequest,
    RebuildPlanResponse,
)
from ...domains.adaptation.service import confirm_rebuild, list_events
from ...domains.plan.service import PreconditionsNotMet
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
    status_code=status.HTTP_201_CREATED,
)
async def post_rebuild(
    payload: RebuildPlanRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> RebuildPlanResponse:
    """Scenario 2.2 — пользователь подтверждает регенерацию.

    Под капотом — `generate_plan` из spec 006: старый план архивируется,
    новый сохраняется как active. Контракт ошибок такой же, как у
    `POST /plans/generate` — 400 `preconditions_not_met`, чтобы PWA-
    клиент мог использовать одну ветку обработки.
    """
    try:
        event, plan, warnings = await confirm_rebuild(
            session, user_id=user.id, target=payload.target
        )
    except PreconditionsNotMet as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.as_http_detail("Заполните профиль перед регенерацией плана"),
        ) from exc

    return RebuildPlanResponse(
        event_id=event.id,
        target_plan=event.target_plan,
        status=event.status,
        plan_id=plan.id,
        warnings=warnings,
    )
