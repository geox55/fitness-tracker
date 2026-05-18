"""Adaptation endpoints — spec 009 §7."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from ...domains.adaptation.schemas import (
    BackgroundCheckResponse,
    PlanRebuildEventList,
    PlanRebuildEventRead,
    RebuildPlanRequest,
    RebuildPlanResponse,
)
from ...domains.adaptation.service import (
    confirm_rebuild,
    list_events,
    run_background_check,
)
from ...domains.plan.service import ActivePlanRaceError, PreconditionsNotMet
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(tags=["adaptation"])

# REQ-03 + REQ-04: служебный cron-эндпоинт. Без user-auth (вызывается
# контейнером api-cleanup или внешним планировщиком из той же docker-
# сети). Ролевая модель в users пока отсутствует, поэтому ограничение
# идёт только сетью — так же, как у /internal/inbody-pdf/templates/stats.
internal_router = APIRouter(prefix="/internal/adaptation", tags=["adaptation-internal"])


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
    except ActivePlanRaceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": exc.code,
                "message": "Параллельный rebuild уже создал активный план. Обновите страницу.",
            },
        ) from exc

    return RebuildPlanResponse(
        event_id=event.id,
        target_plan=event.target_plan,
        status=event.status,
        plan_id=plan.id,
        warnings=warnings,
    )


@internal_router.post(
    "/check-cycles",
    response_model=BackgroundCheckResponse,
)
async def post_check_cycles(session: SessionDep) -> BackgroundCheckResponse:
    """Cron-вход для Scenario 3 (конец цикла) + Scenario 2.3 (force через 7
    дней игнора). Без user_id — проходит по всем пользователям и возвращает
    краткую сводку. Тяжёлой работы здесь нет: переиспользует уже
    скомпонованный rule-based composer спека-006.
    """
    report = await run_background_check(session)
    return BackgroundCheckResponse(
        cycle_end_rebuilt=report.cycle_end_rebuilt,
        force_rebuilt=report.force_rebuilt,
        skipped=report.skipped,
    )
