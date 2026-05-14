"""Workouts endpoints — spec 005."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ...domains.catalog.models import Exercise
from ...domains.workouts.models import ExerciseLog, Workout
from ...domains.workouts.schemas import (
    ExerciseLogRead,
    LogSetRequest,
    StartWorkoutRequest,
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
    workout = Workout(
        user_id=user.id,
        performed_at=datetime.now(UTC),
        status="in_progress",
        origin=payload.origin,
        notes=payload.notes,
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
    exercise = await session.get(Exercise, payload.exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "exercise_not_found", "message": "Упражнение не найдено"},
        )
    log = ExerciseLog(
        workout_id=workout.id,
        exercise_id=payload.exercise_id,
        set_number=payload.set_number,
        reps=payload.reps,
        weight_kg=payload.weight_kg,
        rpe=payload.rpe,
        rest_seconds=payload.rest_seconds,
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
