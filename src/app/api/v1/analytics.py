"""Analytics endpoints — agregaty для главного экрана + spec 010 §9."""

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from ...domain.analytics import SERIES_METRICS
from ...domains.analytics.goal_service import (
    GoalProgress,
    NoGoal,
    get_goal_progress,
)
from ...domains.analytics.exercise_progress_service import (
    ExerciseNotFoundError,
    exercise_progress,
)
from ...domains.analytics.inbody_service import (
    MeasurementNotFoundError,
    compare,
    series,
    to_datetime_inclusive_end,
    to_datetime_inclusive_start,
)
from ...domains.analytics.schemas import (
    CompareMeasurement,
    CompareResponse,
    ExerciseProgressResponse,
    ExerciseProgressWeekItem,
    FieldDeltaSchema,
    ForecastSeries,
    ForecastSeriesPoint,
    GoalProgressEmptyResponse,
    GoalProgressResponse,
    InBodySeriesResponse,
    OverviewResponse,
    SeriesPoint,
    WorkoutsAnalyticsResponse,
    WorkoutsBucket,
)
from ...domains.analytics.service import build_overview
from ...domains.analytics.workouts_service import (
    SUPPORTED_BUCKETS,
    UnsupportedBucketError,
    workouts_buckets,
)
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewResponse)
async def overview(user: CurrentUserDep, session: SessionDep) -> OverviewResponse:
    return await build_overview(session, user_id=user.id)


_METRIC_DESC = (
    "Имя метрики для серии: weight_kg, body_fat_percent, ..."
    " (полный список — см. SERIES_METRICS в domain/analytics)"
)
_FORECAST_DESC = (
    "Включать overlay-прогноз "
    "(только для weight_kg/body_fat_percent/muscle_mass_kg)"
)


@router.get("/inbody", response_model=InBodySeriesResponse)
async def inbody_series(
    user: CurrentUserDep,
    session: SessionDep,
    metric: Annotated[str, Query(description=_METRIC_DESC)],
    from_: Annotated[date | None, Query(alias="from")] = None,
    to: Annotated[date | None, Query()] = None,
    forecast: Annotated[bool, Query(description=_FORECAST_DESC)] = True,
) -> InBodySeriesResponse:
    """REQ-01..03 spec 010: серия одной InBody-метрики + опциональный прогноз."""
    if metric not in SERIES_METRICS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_metric",
                "message": f"Unknown metric '{metric}'. Allowed: {list(SERIES_METRICS)}",
            },
        )
    if from_ is not None and to is not None and from_ > to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_range",
                "message": "from must be ≤ to",
            },
        )

    history, forecast_points = await series(
        session,
        user_id=user.id,
        metric=metric,
        from_=to_datetime_inclusive_start(from_),
        to=to_datetime_inclusive_end(to),
        include_forecast=forecast,
    )

    forecast_block: ForecastSeries | None = None
    if forecast and forecast_points:
        forecast_block = ForecastSeries(
            points=[
                ForecastSeriesPoint(
                    date=p.date,
                    value=p.value,
                    ci_low=p.ci_low,
                    ci_high=p.ci_high,
                )
                for p in forecast_points
            ]
        )

    return InBodySeriesResponse(
        metric=metric,
        points=[SeriesPoint(date=d, value=v) for d, v in history],
        forecast=forecast_block,
    )


@router.get("/inbody/compare", response_model=CompareResponse)
async def inbody_compare(
    user: CurrentUserDep,
    session: SessionDep,
    a: Annotated[uuid.UUID, Query(description="UUID первого замера")],
    b: Annotated[uuid.UUID, Query(description="UUID второго замера")],
) -> CompareResponse:
    """REQ-04 spec 010: дельты между двумя замерами того же пользователя."""
    if a == b:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "same_measurement",
                "message": "a and b must be different measurements",
            },
        )
    try:
        a_row, b_row, deltas = await compare(
            session, user_id=user.id, a_id=a, b_id=b
        )
    except MeasurementNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": exc.code, "message": "Замер не найден"},
        ) from exc

    return CompareResponse(
        a=CompareMeasurement(id=a_row.id, measured_at=a_row.measured_at),
        b=CompareMeasurement(id=b_row.id, measured_at=b_row.measured_at),
        deltas=[
            FieldDeltaSchema(
                field=d.field,
                value_a=d.value_a,
                value_b=d.value_b,
                delta_absolute=d.delta_absolute,
                delta_percent=d.delta_percent,
            )
            for d in deltas
        ],
    )


_BUCKET_DESC = (
    "Группировка периодов: day | week | month. "
    "По умолчанию week — основной кейс из spec 010 §3 Scenario 4."
)


@router.get("/workouts", response_model=WorkoutsAnalyticsResponse)
async def workouts_analytics(
    user: CurrentUserDep,
    session: SessionDep,
    bucket: Annotated[str, Query(description=_BUCKET_DESC)] = "week",
    from_: Annotated[date | None, Query(alias="from")] = None,
    to: Annotated[date | None, Query()] = None,
) -> WorkoutsAnalyticsResponse:
    """REQ-07/08 spec 010: тоннаж и количество тренировок по периодам."""
    if bucket not in SUPPORTED_BUCKETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "unsupported_bucket",
                "message": (
                    f"Bucket {bucket!r} не поддерживается. "
                    f"Допустимые: {list(SUPPORTED_BUCKETS)}"
                ),
            },
        )
    if from_ is not None and to is not None and from_ > to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_range",
                "message": "from must be ≤ to",
            },
        )

    try:
        rows = await workouts_buckets(
            session,
            user_id=user.id,
            bucket=bucket,
            from_=to_datetime_inclusive_start(from_),
            to=to_datetime_inclusive_end(to),
        )
    except UnsupportedBucketError as exc:
        # Дополнительная защита на случай, если whitelist разъехался.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": exc.code, "message": str(exc)},
        ) from exc

    return WorkoutsAnalyticsResponse(
        bucket=bucket,
        items=[
            WorkoutsBucket(
                period_start=ps,
                tonnage_kg=round(tonnage, 2),
                workouts_count=count,
            )
            for ps, tonnage, count in rows
        ],
    )


@router.get(
    "/exercise-progress",
    response_model=ExerciseProgressResponse,
)
async def exercise_progress_endpoint(
    user: CurrentUserDep,
    session: SessionDep,
    exercise_id: Annotated[uuid.UUID, Query(description="UUID упражнения в каталоге")],
    from_: Annotated[date | None, Query(alias="from")] = None,
    to: Annotated[date | None, Query()] = None,
) -> ExerciseProgressResponse:
    """REQ-09 spec 010: best working weight + 1RM по Epley по неделям.

    404 — если такого упражнения нет в каталоге. Пустая история — это не
    ошибка: возвращаем `weeks=[]`, UI рисует empty state с CTA «Добавьте
    тренировку с этим упражнением».
    """
    if from_ is not None and to is not None and from_ > to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_range",
                "message": "from must be ≤ to",
            },
        )
    try:
        result = await exercise_progress(
            session,
            user_id=user.id,
            exercise_id=exercise_id,
            from_=to_datetime_inclusive_start(from_),
            to=to_datetime_inclusive_end(to),
        )
    except ExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": exc.code, "message": "Упражнение не найдено"},
        ) from exc

    return ExerciseProgressResponse(
        exercise_id=result.exercise_id,
        exercise_title=result.exercise_title,
        weeks=[
            ExerciseProgressWeekItem(
                week_start=w.week_start,
                best_weight_kg=w.best_weight_kg,
                best_e1rm_kg=w.best_e1rm_kg,
                sets=w.sets,
                tonnage_kg=w.tonnage_kg,
            )
            for w in result.weeks
        ],
    )


@router.get(
    "/goal-progress",
    response_model=GoalProgressResponse | GoalProgressEmptyResponse,
)
async def goal_progress(
    user: CurrentUserDep,
    session: SessionDep,
) -> GoalProgressResponse | GoalProgressEmptyResponse:
    """REQ-05/06 spec 010: progress bar + ETA для weight_loss / muscle_gain.

    Возвращает один из двух payload'ов:
    - `GoalProgressResponse` — у пользователя цель и таргет заданы,
      есть хотя бы один InBody-замер; ETA опционально (если прогноз
      построился и пересекает target);
    - `GoalProgressEmptyResponse` — UI показывает CTA «Укажите цель в профиле»;
      `reason` подскажет, что именно не заполнено.

    Оба ответа отдаются с HTTP 200: для UI это не «ошибка», а легитимные
    варианты состояния. 4xx сюда не маппится.
    """
    result = await get_goal_progress(session, user_id=user.id)
    if isinstance(result, NoGoal):
        return GoalProgressEmptyResponse(
            reason=result.reason,
            missing_fields=list(result.missing_fields),
        )
    assert isinstance(result, GoalProgress)  # для mypy: union narrowing
    return GoalProgressResponse(
        goal=result.goal,
        start_value=result.start_value,
        current_value=result.current_value,
        target_value=result.target_value,
        progress_percent=result.progress_percent,
        already_reached=result.already_reached,
        started_at=result.started_at,
        eta=result.eta,
        eta_confidence=result.eta_confidence,
    )
