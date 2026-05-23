"""Workouts endpoints — spec 005."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ...domains.catalog.models import Exercise
from ...domains.plan.models import PlanDay, PlanWeek, WorkoutPlan
from ...domains.workouts.models import ExerciseLog, Workout
from ...domains.workouts.schemas import (
    ExerciseLogRead,
    GroupSupersetRequest,
    LogSetRequest,
    StartWorkoutRequest,
    SupersetMutationResponse,
    UngroupSupersetRequest,
    WorkoutListResponse,
    WorkoutPatch,
    WorkoutRead,
    WorkoutSummary,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/workouts", tags=["workouts"])


def _ensure_owner(workout: Workout | None, user_id: uuid.UUID) -> Workout:
    if workout is None or workout.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Тренировка не найдена"},
        )
    return workout


@router.post("", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
async def start_workout(
    payload: StartWorkoutRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> WorkoutRead:
    """spec 005 REQ-01/02/12: старт тренировки.

    Если передан `plan_day_id` — проверяем что день принадлежит активному
    плану пользователя; иначе 404 plan_day_not_found. На стороне БД FK
    стоит ON DELETE SET NULL, так что архивация плана не ломает Workout.
    `origin` принудительно выставляется в `'plan'` при наличии plan_day_id —
    иначе семантика поля противоречит ссылке.
    """
    # spec 015 REQ-02: idempotency-check по client_id.
    # Клиентский retry после потерянного ответа не должен создать дубликат.
    if payload.client_id is not None:
        existing = await session.scalar(
            select(Workout)
            .where(
                Workout.client_id == payload.client_id,
                Workout.user_id == user.id,
            )
            .options(selectinload(Workout.logs))
        )
        if existing is not None:
            return WorkoutRead.model_validate(existing, from_attributes=True)

    plan_day_id = payload.plan_day_id
    origin = payload.origin
    if plan_day_id is not None:
        # PlanDay → PlanWeek → WorkoutPlan: проверяем владельца цепочкой
        # JOIN. selectinload не нужен — нам важен только факт принадлежности.
        owner_check = await session.execute(
            select(PlanDay.id)
            .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
            .join(WorkoutPlan, WorkoutPlan.id == PlanWeek.plan_id)
            .where(
                PlanDay.id == plan_day_id,
                WorkoutPlan.user_id == user.id,
            )
        )
        if owner_check.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "plan_day_not_found",
                    "message": "День плана не найден",
                },
            )
        origin = "plan"

    workout = Workout(
        user_id=user.id,
        performed_at=datetime.now(UTC),
        status="in_progress",
        origin=origin,
        plan_day_id=plan_day_id,
        notes=payload.notes,
        client_id=payload.client_id,
    )
    session.add(workout)
    try:
        await session.flush()
    except IntegrityError as exc:
        # partial unique index не даст создать вторую active
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "active_workout_exists",
                "message": "Уже есть активная тренировка",
            },
        ) from exc
    # Явно строим ответ без обращения к relationship logs (lazy-load в async
    # вызывает MissingGreenlet, а на новой тренировке логи всегда пусты).
    return WorkoutRead(
        id=workout.id,
        performed_at=workout.performed_at,
        finished_at=workout.finished_at,
        status=workout.status,
        origin=workout.origin,
        notes=workout.notes,
        plan_day_id=workout.plan_day_id,
        logs=[],
    )


@router.get("/active", response_model=WorkoutRead | None)
async def get_active(user: CurrentUserDep, session: SessionDep) -> WorkoutRead | None:
    stmt = (
        select(Workout)
        .where(Workout.user_id == user.id, Workout.status == "in_progress")
        .options(selectinload(Workout.logs))
    )
    workout = (await session.execute(stmt)).scalar_one_or_none()
    if workout is None:
        return None
    return WorkoutRead.model_validate(workout, from_attributes=True)


@router.get("", response_model=WorkoutListResponse)
async def list_workouts(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> WorkoutListResponse:
    items_stmt = (
        select(
            Workout,
            func.count(ExerciseLog.id).label("sets_count"),
            func.coalesce(
                func.sum(ExerciseLog.reps * ExerciseLog.weight_kg), 0
            ).label("total_tonnage"),
        )
        .join(ExerciseLog, ExerciseLog.workout_id == Workout.id, isouter=True)
        .where(Workout.user_id == user.id)
        .group_by(Workout.id)
        .order_by(Workout.performed_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = (await session.execute(items_stmt)).all()
    summaries = [
        WorkoutSummary(
            id=row[0].id,
            performed_at=row[0].performed_at,
            finished_at=row[0].finished_at,
            status=row[0].status,
            origin=row[0].origin,
            sets_count=int(row[1] or 0),
            total_tonnage=float(row[2] or 0),
        )
        for row in rows
    ]
    total = (
        await session.execute(
            select(func.count(Workout.id)).where(Workout.user_id == user.id)
        )
    ).scalar_one()
    return WorkoutListResponse(items=summaries, total=int(total))


@router.get("/{workout_id}", response_model=WorkoutRead)
async def get_workout(
    workout_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> WorkoutRead:
    stmt = (
        select(Workout)
        .where(Workout.id == workout_id)
        .options(selectinload(Workout.logs))
    )
    workout = _ensure_owner(
        (await session.execute(stmt)).scalar_one_or_none(), user.id
    )
    return WorkoutRead.model_validate(workout, from_attributes=True)


@router.post("/{workout_id}/logs", response_model=ExerciseLogRead, status_code=201)
async def log_set(
    workout_id: uuid.UUID,
    payload: LogSetRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> ExerciseLogRead:
    workout = _ensure_owner(await session.get(Workout, workout_id), user.id)
    if workout.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "workout_not_in_progress",
                "message": "Тренировка завершена",
            },
        )

    # spec 015 REQ-02: idempotency-check для офлайн-ретрая лога подхода.
    if payload.client_id is not None:
        existing_log = await session.scalar(
            select(ExerciseLog)
            .join(Workout, Workout.id == ExerciseLog.workout_id)
            .where(
                ExerciseLog.client_id == payload.client_id,
                Workout.user_id == user.id,
            )
        )
        if existing_log is not None:
            return ExerciseLogRead.model_validate(
                existing_log, from_attributes=True
            )

    exercise = await session.get(Exercise, payload.exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "exercise_not_found", "message": "Упражнение не найдено"},
        )

    # spec 016 REQ-05: если у этого упражнения в текущей тренировке уже
    # есть лог, и он в составе суперсета — наследуем superset_group_id,
    # чтобы новый подход автоматически попал в ту же группу.
    inherited_group_id = await session.scalar(
        select(ExerciseLog.superset_group_id)
        .where(
            ExerciseLog.workout_id == workout.id,
            ExerciseLog.exercise_id == payload.exercise_id,
            ExerciseLog.superset_group_id.is_not(None),
        )
        .limit(1)
    )

    log = ExerciseLog(
        workout_id=workout.id,
        exercise_id=payload.exercise_id,
        set_number=payload.set_number,
        reps=payload.reps,
        weight_kg=payload.weight_kg,
        rpe=payload.rpe,
        rest_seconds=payload.rest_seconds,
        client_id=payload.client_id,
        superset_group_id=inherited_group_id,
    )
    session.add(log)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "duplicate_set",
                "message": "Подход с таким номером уже зафиксирован",
            },
        ) from exc
    await session.refresh(log)
    return ExerciseLogRead.model_validate(log, from_attributes=True)


@router.delete("/{workout_id}/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    workout_id: uuid.UUID,
    log_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    workout = _ensure_owner(await session.get(Workout, workout_id), user.id)
    log = await session.get(ExerciseLog, log_id)
    if log is None or log.workout_id != workout.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Подход не найден"},
        )
    await session.delete(log)


@router.post("/{workout_id}/finish", response_model=WorkoutRead)
async def finish_workout(
    workout_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> WorkoutRead:
    stmt = (
        select(Workout)
        .where(Workout.id == workout_id)
        .options(selectinload(Workout.logs))
    )
    workout = _ensure_owner(
        (await session.execute(stmt)).scalar_one_or_none(), user.id
    )
    if workout.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "workout_not_in_progress",
                "message": "Тренировка уже завершена",
            },
        )
    workout.status = "completed"
    workout.finished_at = datetime.now(UTC)
    await session.flush()
    return WorkoutRead.model_validate(workout, from_attributes=True)


@router.post("/{workout_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_workout(
    workout_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    workout = _ensure_owner(await session.get(Workout, workout_id), user.id)
    if workout.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "workout_not_in_progress",
                "message": "Тренировка уже завершена",
            },
        )
    workout.status = "cancelled"
    workout.finished_at = datetime.now(UTC)


@router.patch("/{workout_id}", response_model=WorkoutRead)
async def update_workout(
    workout_id: uuid.UUID,
    payload: WorkoutPatch,
    user: CurrentUserDep,
    session: SessionDep,
) -> WorkoutRead:
    """Поправить notes / performed_at / finished_at у существующей тренировки.

    Сценарий: пользователь забыл закрыть «1-секундную» тренировку и хочет
    выставить нормальную длительность, либо просто дописать заметку. Статус
    и origin тут не меняем — для статуса есть finish/cancel.
    """
    stmt = (
        select(Workout)
        .where(Workout.id == workout_id)
        .options(selectinload(Workout.logs))
    )
    workout = _ensure_owner(
        (await session.execute(stmt)).scalar_one_or_none(), user.id
    )

    patch_data = payload.model_dump(exclude_unset=True)

    if "notes" in patch_data:
        workout.notes = patch_data["notes"]
    if "performed_at" in patch_data:
        new_performed = patch_data["performed_at"]
        if new_performed is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "invalid_performed_at",
                    "message": "Время начала обязательно",
                },
            )
        workout.performed_at = new_performed
    if "finished_at" in patch_data:
        new_finished = patch_data["finished_at"]
        # Для завершённой тренировки finished_at обязателен — сбросить нельзя.
        if new_finished is None and workout.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "invalid_finished_at",
                    "message": "У завершённой тренировки должно быть время окончания",
                },
            )
        workout.finished_at = new_finished

    if (
        workout.finished_at is not None
        and workout.performed_at > workout.finished_at
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "invalid_range",
                "message": "Окончание не может быть раньше начала",
            },
        )

    await session.flush()
    return WorkoutRead.model_validate(workout, from_attributes=True)


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    workout = _ensure_owner(await session.get(Workout, workout_id), user.id)
    await session.delete(workout)


# --- Суперсеты (spec 016) ---------------------------------------------------


@router.post(
    "/{workout_id}/supersets/group",
    response_model=SupersetMutationResponse,
)
async def group_superset(
    workout_id: uuid.UUID,
    payload: GroupSupersetRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> SupersetMutationResponse:
    """spec 016 REQ-03. Объединяет логи двух упражнений в одну группу:
    выставляет всем общий `superset_group_id`. Если хотя бы один лог
    уже в группе — переиспользуем её id, чтобы не плодить дубликаты при
    повторных вызовах (idempotency-friendly)."""
    workout = _ensure_owner(await session.get(Workout, workout_id), user.id)

    rows = (
        await session.execute(
            select(ExerciseLog).where(
                ExerciseLog.workout_id == workout.id,
                ExerciseLog.exercise_id.in_(payload.exercise_ids),
            )
        )
    ).scalars().all()
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "no_logs_for_exercises",
                "message": "Для указанных упражнений нет подходов в этой тренировке",
            },
        )

    # Если у любого из существующих логов уже есть group_id — берём его.
    existing_group_id = next(
        (r.superset_group_id for r in rows if r.superset_group_id is not None),
        None,
    )
    group_id = existing_group_id or uuid.uuid4()
    updated = 0
    for r in rows:
        if r.superset_group_id != group_id:
            r.superset_group_id = group_id
            updated += 1
    await session.flush()
    return SupersetMutationResponse(group_id=group_id, logs_updated=updated)


@router.post(
    "/{workout_id}/supersets/ungroup",
    response_model=SupersetMutationResponse,
)
async def ungroup_superset(
    workout_id: uuid.UUID,
    payload: UngroupSupersetRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> SupersetMutationResponse:
    """spec 016 REQ-04. Сбрасывает `superset_group_id` всех логов с
    указанным group_id в этой тренировке."""
    workout = _ensure_owner(await session.get(Workout, workout_id), user.id)
    rows = (
        await session.execute(
            select(ExerciseLog).where(
                ExerciseLog.workout_id == workout.id,
                ExerciseLog.superset_group_id == payload.group_id,
            )
        )
    ).scalars().all()
    for r in rows:
        r.superset_group_id = None
    await session.flush()
    return SupersetMutationResponse(group_id=None, logs_updated=len(rows))
