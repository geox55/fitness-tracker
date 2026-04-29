"""Catalog endpoints — упражнения. Spec 004."""

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, or_, select

from ...domains.catalog.models import Exercise
from ...domains.catalog.schemas import (
    ExerciseDetail,
    ExerciseListResponse,
    ExerciseSummary,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/exercises", tags=["catalog"])


@router.get("", response_model=ExerciseListResponse)
async def list_exercises(
    _user: CurrentUserDep,
    session: SessionDep,
    q: str | None = Query(default=None, min_length=2, max_length=64),
    muscle_group: str | None = None,
    body_region: str | None = None,
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ExerciseListResponse:
    stmt = select(Exercise)
    count_stmt = select(func.count(Exercise.id))

    filters = []
    if q:
        like = f"%{q.lower()}%"
        filters.append(
            or_(
                func.lower(Exercise.exercise_name).like(like),
                func.lower(Exercise.exercise_name_ru).like(like),
            )
        )
    if muscle_group:
        filters.append(Exercise.primary_muscle_group == muscle_group)
    if body_region:
        filters.append(Exercise.body_region == body_region)

    for f in filters:
        stmt = stmt.where(f)
        count_stmt = count_stmt.where(f)

    total = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        stmt.order_by(Exercise.exercise_name)
        .offset(offset)
        .limit(limit)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return ExerciseListResponse(
        items=[ExerciseSummary.model_validate(r) for r in rows],
        total=int(total),
    )


@router.get("/{exercise_id}", response_model=ExerciseDetail)
async def get_exercise(
    exercise_id: uuid.UUID,
    _user: CurrentUserDep,
    session: SessionDep,
) -> ExerciseDetail:
    ex = await session.get(Exercise, exercise_id)
    if ex is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Упражнение не найдено"},
        )
    return ExerciseDetail.model_validate(ex)
