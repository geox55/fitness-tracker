"""Plans endpoints — spec 006 §9.

POST /plans/generate         — собрать новый план (REQ-12 ручная регенерация)
GET  /plans/active           — текущий активный план
GET  /plans/{id}             — любой план пользователя
POST /plans/{id}/archive     — пометить как archived
GET  /plans?status=archived  — история планов
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from ...domains.plan.models import PlanExercise, WorkoutPlan
from ...domains.plan.schemas import (
    PlanDayRead,
    PlanExerciseRead,
    PlanGenerateRequest,
    PlanListResponse,
    PlanRead,
    PlanSummary,
    PlanWeekRead,
)
from ...domains.plan.service import (
    ActivePlanRaceError,
    PlanNotFoundError,
    PreconditionsNotMet,
    archive,
    generate_plan,
    get_active,
    get_by_id,
    list_for_user,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/plans", tags=["plans"])


def _build_plan_read(
    plan: WorkoutPlan, *, warnings: list[str] | None = None
) -> PlanRead:
    """Сериализатор ORM → PlanRead.

    Делаем вручную, потому что:
    - у PlanExercise имя упражнения живёт через FK → Exercise;
    - у WorkoutPlan нет поля warnings (это одноразовая ответная мета).
    Все relationship должны быть eager-loaded (см. `_select_with_relations`),
    иначе словим SQL-call в синхронном коде.
    """
    weeks: list[PlanWeekRead] = []
    for week in plan.weeks:
        days: list[PlanDayRead] = []
        for day in week.days:
            exercises: list[PlanExerciseRead] = []
            for ex in day.exercises:
                exercises.append(_build_exercise_read(ex))
            days.append(
                PlanDayRead(
                    id=day.id,
                    day_no=day.day_no,
                    name=day.name,
                    type=day.type,
                    exercises=exercises,
                )
            )
        weeks.append(PlanWeekRead(id=week.id, week_no=week.week_no, days=days))
    return PlanRead.model_validate(
        {
            "id": plan.id,
            "status": plan.status,
            "generated_at": plan.generated_at,
            "valid_until": plan.valid_until,
            "goal": plan.goal,
            "training_level": plan.training_level,
            "frequency": plan.frequency,
            "model_version": plan.model_version,
            "weeks": weeks,
            "warnings": list(warnings or []),
        }
    )


def _build_exercise_read(ex: PlanExercise) -> PlanExerciseRead:
    """ORM → PlanExerciseRead с подмешиванием name из каталога.

    RU-имя приоритетнее EN (UI ожидает локализованное), как и везде
    в `pwa/lib/data/api/catalog_api.dart::displayName`.
    """
    name = ex.exercise.exercise_name_ru or ex.exercise.exercise_name
    return PlanExerciseRead(
        id=ex.id,
        exercise_id=ex.exercise_id,
        exercise_name=name,
        order_no=ex.order_no,
        target_sets=ex.target_sets,
        target_reps_min=ex.target_reps_min,
        target_reps_max=ex.target_reps_max,
        target_rpe=ex.target_rpe,
        rest_seconds=ex.rest_seconds,
        target_weight_kg=(
            float(ex.target_weight_kg) if ex.target_weight_kg is not None else None
        ),
        notes=ex.notes,
    )


@router.post(
    "/generate",
    response_model=PlanRead,
    status_code=status.HTTP_201_CREATED,
)
async def generate(
    user: CurrentUserDep,
    session: SessionDep,
    payload: PlanGenerateRequest | None = None,
) -> PlanRead:
    """REQ-01/12 spec 006: сгенерировать новый план.

    Поведение:
    - 201 + PlanRead с warnings (если composer что-то пометил, например
      «оборудование ограничено»);
    - 400 preconditions_not_met если профиль не заполнен.
    """
    override = payload.override if payload is not None else None
    try:
        plan, warnings = await generate_plan(
            session,
            user_id=user.id,
            override_goal=override.goal if override else None,
            override_level=override.training_level if override else None,
            override_frequency=override.training_frequency if override else None,
            override_equipment=override.equipment_available if override else None,
        )
    except PreconditionsNotMet as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.as_http_detail("Заполните профиль перед генерацией плана"),
        ) from exc
    except ActivePlanRaceError as exc:
        # Двойной клик / параллельный запрос — один из них уже создал план.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": exc.code,
                "message": "Параллельная генерация уже создала активный план. Обновите страницу.",
            },
        ) from exc

    # После flush объект plan ещё не имеет загруженных weeks через
    # selectinload — берём через get_by_id с eager-load.
    full = await get_by_id(session, user_id=user.id, plan_id=plan.id)
    assert full is not None
    return _build_plan_read(full, warnings=warnings)


@router.get("/active", response_model=PlanRead)
async def active(user: CurrentUserDep, session: SessionDep) -> PlanRead:
    plan = await get_active(session, user_id=user.id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "no_active_plan", "message": "Активного плана нет"},
        )
    return _build_plan_read(plan)


@router.get("/{plan_id}", response_model=PlanRead)
async def get_one(
    plan_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> PlanRead:
    plan = await get_by_id(session, user_id=user.id, plan_id=plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "plan_not_found", "message": "План не найден"},
        )
    return _build_plan_read(plan)


@router.post("/{plan_id}/archive", response_model=PlanRead)
async def archive_one(
    plan_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> PlanRead:
    try:
        await archive(session, user_id=user.id, plan_id=plan_id)
    except PlanNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": exc.code, "message": "План не найден"},
        ) from exc
    # Перечитываем с eager-load, потому что archive() не догружает relations.
    full = await get_by_id(session, user_id=user.id, plan_id=plan_id)
    assert full is not None
    return _build_plan_read(full)


@router.get("", response_model=PlanListResponse)
async def list_plans(
    user: CurrentUserDep,
    session: SessionDep,
    plan_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PlanListResponse:
    if plan_status is not None and plan_status not in ("active", "archived"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_status",
                "message": "status должен быть active или archived",
            },
        )
    rows, total = await list_for_user(
        session,
        user_id=user.id,
        status=plan_status,
        limit=limit,
        offset=offset,
    )
    return PlanListResponse(
        items=[PlanSummary.model_validate(r, from_attributes=True) for r in rows],
        total=total,
    )
