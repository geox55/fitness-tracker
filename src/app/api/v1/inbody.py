"""InBody endpoints — spec 003 (без PDF-парсинга, см. spec 013)."""

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from ...domains.inbody.schemas import (
    CreateMeasurementRequest,
    MeasurementListResponse,
    MeasurementRead,
)
from ...domains.inbody.service import (
    HeightUnknownError,
    SexUnknownError,
    create_manual,
    delete,
    get_for_user,
    list_for_user,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/inbody/measurements", tags=["inbody"])


@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
async def create(
    payload: CreateMeasurementRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> MeasurementRead:
    try:
        measurement = await create_manual(
            session,
            user_id=user.id,
            payload=payload.model_dump(exclude_none=False),
        )
    except HeightUnknownError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": exc.code,
                "message": "Укажите рост в профиле или передайте height_cm",
            },
        ) from exc
    except SexUnknownError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": exc.code,
                "message": "Укажите пол в профиле или передайте sex",
            },
        ) from exc
    return MeasurementRead.model_validate(measurement)


@router.get("", response_model=MeasurementListResponse)
async def list_measurements(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> MeasurementListResponse:
    items, total = await list_for_user(
        session, user_id=user.id, limit=limit, offset=offset
    )
    return MeasurementListResponse(
        items=[MeasurementRead.model_validate(m) for m in items],
        total=total,
    )


@router.get("/{measurement_id}", response_model=MeasurementRead)
async def get_one(
    measurement_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> MeasurementRead:
    m = await get_for_user(session, user_id=user.id, measurement_id=measurement_id)
    if m is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Измерение не найдено"},
        )
    return MeasurementRead.model_validate(m)


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    measurement_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    m = await get_for_user(session, user_id=user.id, measurement_id=measurement_id)
    if m is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Измерение не найдено"},
        )
    await delete(session, m)
