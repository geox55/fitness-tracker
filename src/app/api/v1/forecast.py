"""Forecast endpoints — spec 008."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from ...domain.forecast import Override
from ...domain.forecast.predictor import ForecastBundle, ForecastPoint
from ...domains.forecast.schemas import (
    ForecastMetrics,
    ForecastResponse,
    HistoryEvaluation,
    HistoryItem,
    HistoryResponse,
    WhatIfRequest,
)
from ...domains.forecast.schemas import (
    ForecastPoint as ForecastPointSchema,
)
from ...domains.forecast.service import (
    NotEnoughInBodyError,
    get_forecast,
    list_history,
    what_if_forecast,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/forecast/inbody", tags=["forecast"])


def _parse_horizons(raw: str | None) -> tuple[int, ...]:
    if raw is None or not raw.strip():
        return (1, 2, 4)
    try:
        parts = [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_horizons", "message": "horizons must be integers"},
        ) from exc
    if not parts or any(h not in (1, 2, 4) for h in parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_horizons",
                "message": "Allowed horizons: 1, 2, 4",
            },
        )
    # Дедупликация + сортировка для детерминированного ответа.
    return tuple(sorted(set(parts)))


def _serialize(
    bundle: ForecastBundle,
    *,
    generated_at: datetime,
    based_on_inbody_id: UUID,
) -> ForecastResponse:
    def _pts(series_points: tuple[ForecastPoint, ...]) -> list[ForecastPointSchema]:
        return [
            ForecastPointSchema(
                horizon_weeks=p.horizon_weeks,
                point=p.point,
                ci_low=p.ci_low,
                ci_high=p.ci_high,
            )
            for p in series_points
        ]

    return ForecastResponse(
        generated_at=generated_at,
        model_version=bundle.model_version,
        based_on_inbody_id=based_on_inbody_id,
        confidence=bundle.confidence,
        fallback=bundle.fallback,
        what_if=bundle.what_if,
        metrics=ForecastMetrics(
            weight_kg=_pts(bundle.weight_kg.points),
            body_fat_percent=_pts(bundle.body_fat_percent.points),
            muscle_mass_kg=_pts(bundle.muscle_mass_kg.points),
        ),
        interpretation=bundle.interpretation,
    )


@router.get("", response_model=ForecastResponse)
async def get_inbody_forecast(
    user: CurrentUserDep,
    session: SessionDep,
    horizons: str | None = Query(default=None, description="CSV из 1,2,4"),
) -> ForecastResponse:
    parsed = _parse_horizons(horizons)
    try:
        bundle, generated_at, based_on_id = await get_forecast(
            session, user_id=user.id, horizons=parsed
        )
    except NotEnoughInBodyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "not_enough_data",
                "message": "Добавьте InBody, чтобы увидеть прогноз",
            },
        ) from exc
    return _serialize(
        bundle, generated_at=generated_at, based_on_inbody_id=based_on_id
    )


@router.post("/what-if", response_model=ForecastResponse)
async def post_what_if(
    payload: WhatIfRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> ForecastResponse:
    horizons = tuple(sorted(set(payload.horizons))) or (1, 2, 4)
    if any(h not in (1, 2, 4) for h in horizons):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_horizons",
                "message": "Allowed horizons: 1, 2, 4",
            },
        )
    override = Override(
        training_frequency=payload.override.training_frequency,
        calories_offset_kcal=payload.override.calories_offset_kcal,
    )
    try:
        bundle, generated_at, based_on_id = await what_if_forecast(
            session,
            user_id=user.id,
            horizons=horizons,
            override=override,
        )
    except NotEnoughInBodyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "not_enough_data",
                "message": "Добавьте InBody, чтобы увидеть прогноз",
            },
        ) from exc
    return _serialize(
        bundle, generated_at=generated_at, based_on_inbody_id=based_on_id
    )


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> HistoryResponse:
    paired, total = await list_history(
        session, user_id=user.id, limit=limit, offset=offset
    )
    items: list[HistoryItem] = []
    for f, ev in paired:
        items.append(
            HistoryItem(
                id=f.id,
                generated_at=f.generated_at,
                based_on_inbody_id=f.based_on_inbody_id,
                target_metric=f.target_metric,
                horizon_weeks=int(f.horizon_weeks),
                point=float(f.point_estimate),
                ci_low=float(f.ci_low),
                ci_high=float(f.ci_high),
                confidence=f.confidence,
                model_version=f.model_version,
                fallback=f.fallback,
                what_if=f.what_if,
                evaluation=(
                    HistoryEvaluation(
                        actual_inbody_id=ev.actual_inbody_id,
                        absolute_error=float(ev.absolute_error),
                        within_ci=ev.within_ci,
                        evaluated_at=ev.evaluated_at,
                    )
                    if ev is not None
                    else None
                ),
            )
        )
    return HistoryResponse(items=items, total=total)
