"""Catalog endpoints — упражнения. Spec 004 + spec 014.

Маршруты ordering-sensitive: `/favorites`, `/mine`, `/{exercise_id}/favorite`
должны быть зарегистрированы ДО `/{exercise_id}`, иначе FastAPI попытается
матчить их как UUID и вернёт 422.
"""

import uuid

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import case, exists, func, literal, or_, select

from ...domains.catalog.favorites_service import (
    add_favorite,
    list_favorites,
    remove_favorite,
)
from ...domains.catalog.models import Exercise, UserExerciseFavorite
from ...domains.catalog.owned_service import (
    create_owned,
    delete_owned,
    list_owned,
    update_owned,
)
from ...domains.catalog.schemas import (
    ExerciseCreateRequest,
    ExerciseDetail,
    ExerciseListResponse,
    ExerciseSummary,
    ExerciseUpdateRequest,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/exercises", tags=["catalog"])


def _favorite_exists(user_id: uuid.UUID):
    """Скалярный EXISTS: «есть ли строка в user_exercise_favorites
    для user_id и текущего Exercise.id». Используется и для is_favorite,
    и для favorites-first сортировки."""
    return exists(
        select(literal(1)).where(
            UserExerciseFavorite.user_id == user_id,
            UserExerciseFavorite.exercise_id == Exercise.id,
        )
    )


def _to_summary(
    ex: Exercise, *, is_favorite: bool, current_user_id: uuid.UUID
) -> ExerciseSummary:
    return ExerciseSummary.model_validate(
        {
            **ex.__dict__,
            "is_favorite": is_favorite,
            "is_mine": ex.owner_id == current_user_id,
        },
        from_attributes=False,
    )


# ---- /exercises/favorites & /exercises/mine — ДО /{exercise_id} ----------


@router.get("/favorites", response_model=ExerciseListResponse)
async def list_my_favorites(
    user: CurrentUserDep, session: SessionDep
) -> ExerciseListResponse:
    items = await list_favorites(session, user_id=user.id)
    summaries = [
        _to_summary(ex, is_favorite=True, current_user_id=user.id) for ex in items
    ]
    return ExerciseListResponse(items=summaries, total=len(summaries))


@router.get("/mine", response_model=ExerciseListResponse)
async def list_my_exercises(
    user: CurrentUserDep, session: SessionDep
) -> ExerciseListResponse:
    items = await list_owned(session, user_id=user.id)
    # Для своих is_favorite определяется отдельным запросом — на одного
    # пользователя список редко превышает десятки, тяжёлого JOIN не делаем.
    fav_stmt = select(UserExerciseFavorite.exercise_id).where(
        UserExerciseFavorite.user_id == user.id
    )
    fav_ids: set[uuid.UUID] = set(
        (await session.execute(fav_stmt)).scalars().all()
    )
    summaries = [
        _to_summary(ex, is_favorite=(ex.id in fav_ids), current_user_id=user.id)
        for ex in items
    ]
    return ExerciseListResponse(items=summaries, total=len(summaries))


@router.post(
    "/{exercise_id}/favorite",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def add_to_favorites(
    exercise_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> Response:
    ex = await session.get(Exercise, exercise_id)
    # Чужое пользовательское упражнение для текущего user'а не существует —
    # отдаём 404 (не 403), чтобы не утекало знание о существовании.
    if ex is None or (ex.owner_id is not None and ex.owner_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Упражнение не найдено"},
        )
    await add_favorite(session, user_id=user.id, exercise_id=exercise_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{exercise_id}/favorite",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def remove_from_favorites(
    exercise_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> Response:
    # Идемпотентность: отсутствующая запись — не ошибка.
    await remove_favorite(session, user_id=user.id, exercise_id=exercise_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- /exercises — листинг (глобал + свои текущего юзера) ------------------


@router.get("", response_model=ExerciseListResponse)
async def list_exercises(
    user: CurrentUserDep,
    session: SessionDep,
    q: str | None = Query(default=None, min_length=2, max_length=64),
    muscle_group: str | None = None,
    body_region: str | None = None,
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ExerciseListResponse:
    fav_expr = _favorite_exists(user.id)
    is_fav_col = case((fav_expr, True), else_=False).label("is_favorite")

    stmt = select(Exercise, is_fav_col)
    count_stmt = select(func.count(Exercise.id))

    # Базовый фильтр видимости: глобальные (owner_id IS NULL) + свои.
    visibility = or_(Exercise.owner_id.is_(None), Exercise.owner_id == user.id)
    filters = [visibility]
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

    # Spec 014 §3 Sc.3: избранные в верху текущей выборки.
    stmt = (
        stmt.order_by(fav_expr.desc(), Exercise.exercise_name)
        .offset(offset)
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    items = [
        _to_summary(ex, is_favorite=bool(is_fav), current_user_id=user.id)
        for ex, is_fav in rows
    ]
    return ExerciseListResponse(items=items, total=int(total))


# ---- CRUD «свои упражнения» ----------------------------------------------


@router.post(
    "",
    response_model=ExerciseSummary,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_exercise(
    payload: ExerciseCreateRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> ExerciseSummary:
    ex = await create_owned(
        session, user_id=user.id, fields=payload.model_dump()
    )
    return _to_summary(ex, is_favorite=False, current_user_id=user.id)


@router.patch("/{exercise_id}", response_model=ExerciseSummary)
async def patch_my_exercise(
    exercise_id: uuid.UUID,
    payload: ExerciseUpdateRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> ExerciseSummary:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        # Пустой PATCH — отдаём текущее состояние, не делая UPDATE.
        ex = await session.get(Exercise, exercise_id)
        if ex is None or ex.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": "Упражнение не найдено"},
            )
    else:
        ex = await update_owned(
            session, user_id=user.id, exercise_id=exercise_id, changes=changes
        )
        if ex is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": "Упражнение не найдено"},
            )
    # is_favorite после редактирования не меняется, но честнее перечитать.
    fav_stmt = select(literal(1)).where(
        UserExerciseFavorite.user_id == user.id,
        UserExerciseFavorite.exercise_id == ex.id,
    )
    is_fav = (await session.execute(fav_stmt)).first() is not None
    return _to_summary(ex, is_favorite=is_fav, current_user_id=user.id)


@router.delete(
    "/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_my_exercise(
    exercise_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> Response:
    ok = await delete_owned(
        session, user_id=user.id, exercise_id=exercise_id
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Упражнение не найдено"},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{exercise_id}", response_model=ExerciseDetail)
async def get_exercise(
    exercise_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> ExerciseDetail:
    ex = await session.get(Exercise, exercise_id)
    # Глобальные доступны всем; пользовательские — только владельцу.
    if ex is None or (ex.owner_id is not None and ex.owner_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Упражнение не найдено"},
        )
    return ExerciseDetail.model_validate(ex)
