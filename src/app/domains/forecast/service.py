"""БД-обвязка прогноза InBody — spec 008.

Чистая логика (predictor + features) — в `app.domain.forecast`. Здесь только:
- загрузка истории из БД,
- сборка `FeatureSnapshot`,
- кэширование (NFR-02): возвращаем последний форкаст моложе 24ч, если ничего
  не изменилось (тот же based_on_inbody_id и не what-if),
- сохранение прогноза и evaluation.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.forecast import (
    FeatureSnapshot,
    InBodyPoint,
    Override,
    PredictorInput,
    TrainingAggregate,
    build_feature_snapshot,
    build_forecast,
    evaluate_forecast,
)
from ...domain.forecast.features import serialize_features
from ...domain.forecast.predictor import (
    DEFAULT_HORIZONS,
    ForecastBundle,
    NotEnoughDataError,
)
from ..inbody.models import InBodyMeasurement
from ..profile.models import UserProfile
from ..workouts.models import ExerciseLog, Workout
from .models import ForecastEvaluation, InBodyForecast

_log = logging.getLogger("app.forecast")

CACHE_TTL = timedelta(hours=24)  # NFR-02
EVALUATION_WINDOW = timedelta(days=3)  # Scenario 3: ±3 дня от T+horizon


class ForecastError(Exception):
    code: str = "forecast_error"


class NotEnoughInBodyError(ForecastError):
    """REQ-08: ни одного измерения — 404."""

    code = "not_enough_data"


# ---------------------------------------------------------------------------
# Загрузка фичей
# ---------------------------------------------------------------------------


async def _load_inbody_history(
    session: AsyncSession, *, user_id: uuid.UUID, weeks: int = 16
) -> list[InBodyMeasurement]:
    """Берём всё за последние N недель — этого хватит и для baseline, и для
    cold-start: дальше история теряет актуальность (Edge case §10)."""
    since = datetime.now(UTC) - timedelta(weeks=weeks)
    stmt = (
        select(InBodyMeasurement)
        .where(
            InBodyMeasurement.user_id == user_id,
            InBodyMeasurement.measured_at >= since,
        )
        .order_by(InBodyMeasurement.measured_at.asc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def _load_training_weeks(
    session: AsyncSession, *, user_id: uuid.UUID, weeks: int = 8, now: datetime
) -> list[TrainingAggregate]:
    """Агрегируем тренировки по ISO-неделям. Возвращаем только завершённые
    (status='completed' или 'auto_finished'); cancelled/in_progress исключаем.
    """
    since = now - timedelta(weeks=weeks)
    stmt = (
        select(
            func.date_trunc("week", Workout.performed_at).label("week_start"),
            func.count(Workout.id.distinct()).label("count"),
            func.coalesce(
                func.sum(ExerciseLog.reps * ExerciseLog.weight_kg), 0
            ).label("tonnage"),
        )
        .select_from(Workout)
        .outerjoin(ExerciseLog, ExerciseLog.workout_id == Workout.id)
        .where(
            Workout.user_id == user_id,
            Workout.performed_at >= since,
            Workout.status.in_(("completed", "auto_finished")),
        )
        .group_by("week_start")
        .order_by("week_start")
    )
    rows = (await session.execute(stmt)).all()
    out: list[TrainingAggregate] = []
    for week_start, count, tonnage in rows:
        out.append(
            TrainingAggregate(
                week_start=week_start,
                tonnage_kg=float(tonnage or 0),
                count=int(count),
                # avg_duration не считаем — Workout.finished_at часто null;
                # в дипломе можно расширить, MVP полагается на count и tonnage.
                avg_duration_min=0.0,
            )
        )
    return out


def _to_inbody_points(rows: list[InBodyMeasurement]) -> list[InBodyPoint]:
    return [
        InBodyPoint(
            measured_at=r.measured_at,
            weight_kg=float(r.weight_kg),
            body_fat_percent=float(r.body_fat_percent),
            muscle_mass_kg=(
                float(r.muscle_mass_kg) if r.muscle_mass_kg is not None else None
            ),
        )
        for r in rows
    ]


def _age_years(profile: UserProfile | None, now: datetime) -> int | None:
    if profile is None or profile.birth_date is None:
        return None
    bd = profile.birth_date
    today = now.date()
    years = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    return max(0, years)


async def _build_snapshot(
    session: AsyncSession, *, user_id: uuid.UUID, now: datetime
) -> tuple[FeatureSnapshot, list[InBodyMeasurement]]:
    history = await _load_inbody_history(session, user_id=user_id)
    if not history:
        raise NotEnoughInBodyError("user has no inbody measurements")

    profile = await session.get(UserProfile, user_id)
    weeks = await _load_training_weeks(session, user_id=user_id, now=now)

    snap = build_feature_snapshot(
        inbody_history=_to_inbody_points(history),
        training_weeks=weeks,
        # Поля питания из проекта удалены, fed как None — фичи predictor'а
        # для них имеют ветку «нет данных».
        target_calories_kcal=None,
        actual_calories_kcal=None,
        goal=profile.goal if profile else None,
        training_frequency=profile.training_frequency if profile else None,
        sex=profile.sex if profile else None,
        age_years=_age_years(profile, now),
        height_cm=float(profile.height_cm) if profile and profile.height_cm else None,
        # У нас в моделях нет audit-лога смены цели — пока оставляем None.
        # TODO(spec 002): добавить goal_changed_at в UserProfile или audit-trail.
        goal_changed_within_days=None,
        now=now,
    )
    return snap, history


# ---------------------------------------------------------------------------
# Главный flow: get / what-if
# ---------------------------------------------------------------------------


async def _find_cached(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    based_on_inbody_id: uuid.UUID,
    now: datetime,
) -> list[InBodyForecast]:
    """Возвращаем кэшированный батч, если он моложе CACHE_TTL и привязан к тому
    же InBody. Если есть — это все 9 точек одного forecast-batch (3 метрики × 3
    горизонта по умолчанию)."""
    cutoff = now - CACHE_TTL
    stmt = (
        select(InBodyForecast)
        .where(
            InBodyForecast.user_id == user_id,
            InBodyForecast.based_on_inbody_id == based_on_inbody_id,
            InBodyForecast.what_if.is_(False),
            InBodyForecast.generated_at >= cutoff,
        )
        .order_by(InBodyForecast.generated_at.desc())
    )
    rows = list((await session.execute(stmt)).scalars().all())
    if not rows:
        return []
    # Берём батч с самым свежим generated_at — все строки одного батча имеют
    # один generated_at (он проставляется в сохранении единым значением).
    latest_gen = rows[0].generated_at
    return [r for r in rows if r.generated_at == latest_gen]


def _bundle_to_rows(
    bundle: ForecastBundle,
    *,
    user_id: uuid.UUID,
    based_on_inbody_id: uuid.UUID,
    generated_at: datetime,
    input_features: dict[str, Any],
) -> list[InBodyForecast]:
    rows: list[InBodyForecast] = []
    series = (bundle.weight_kg, bundle.body_fat_percent, bundle.muscle_mass_kg)
    for s in series:
        for p in s.points:
            rows.append(
                InBodyForecast(
                    user_id=user_id,
                    generated_at=generated_at,
                    based_on_inbody_id=based_on_inbody_id,
                    horizon_weeks=p.horizon_weeks,
                    target_metric=s.target_metric,
                    point_estimate=Decimal(str(p.point)),
                    ci_low=Decimal(str(p.ci_low)),
                    ci_high=Decimal(str(p.ci_high)),
                    confidence=bundle.confidence,
                    model_version=bundle.model_version,
                    input_features=input_features,
                    fallback=bundle.fallback,
                    what_if=bundle.what_if,
                    interpretation=bundle.interpretation,
                )
            )
    return rows


async def get_forecast(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    now: datetime | None = None,
) -> tuple[ForecastBundle, datetime, uuid.UUID]:
    """GET /forecast/inbody. С кэшем (NFR-02).

    Возвращает (bundle, generated_at, based_on_inbody_id).
    """
    now = now or datetime.now(UTC)
    snap, history = await _build_snapshot(session, user_id=user_id, now=now)
    based_on_id = history[-1].id

    cached = await _find_cached(
        session, user_id=user_id, based_on_inbody_id=based_on_id, now=now
    )
    if cached:
        # Воссоздаём bundle из БД-строк, не пересчитываем.
        return _rows_to_bundle(cached, horizons=horizons), cached[0].generated_at, based_on_id

    bundle = _run_predictor(snap, horizons=horizons, override=None)
    generated_at = now
    rows = _bundle_to_rows(
        bundle,
        user_id=user_id,
        based_on_inbody_id=based_on_id,
        generated_at=generated_at,
        input_features=serialize_features(snap),
    )
    for r in rows:
        session.add(r)
    await session.flush()
    return bundle, generated_at, based_on_id


async def what_if_forecast(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    horizons: tuple[int, ...],
    override: Override,
    now: datetime | None = None,
) -> tuple[ForecastBundle, datetime, uuid.UUID]:
    """POST /forecast/inbody/what-if. Без кэша — всегда пересчитываем."""
    now = now or datetime.now(UTC)
    snap, history = await _build_snapshot(session, user_id=user_id, now=now)
    based_on_id = history[-1].id
    bundle = _run_predictor(snap, horizons=horizons, override=override)

    rows = _bundle_to_rows(
        bundle,
        user_id=user_id,
        based_on_inbody_id=based_on_id,
        generated_at=now,
        input_features=serialize_features(snap)
        | {
            "override_training_frequency": override.training_frequency,
            "override_calories_offset_kcal": override.calories_offset_kcal,
        },
    )
    for r in rows:
        session.add(r)
    await session.flush()
    return bundle, now, based_on_id


def _run_predictor(
    snap: FeatureSnapshot,
    *,
    horizons: tuple[int, ...],
    override: Override | None,
) -> ForecastBundle:
    """REQ-12: пробуем ML (если артефакт обучен и достаточно истории) →
    при любой ошибке инференса откатываемся к baseline.

    Условие применения ML:
    - artefact на диске есть (`MlPredictor.load()` вернёт не None);
    - история ≥4 InBody (cold-start уходит в baseline, как в spec 008 Sc.2);
    - what-if (override) сейчас остаётся на baseline — ML не училась на
      override-фичах, и подмешивать sample-уровневую коррекцию некорректно.

    `MlPredictor.load()` лениво и кэшируется (`@lru_cache`); первый вызов
    подгружает joblib + boosters в память. На последующие — мгновенно.
    """
    payload = PredictorInput(
        snapshot=snap, horizons=horizons, override=override, force_baseline=False
    )

    if override is None and len(snap.inbody_history) >= 4:
        ml = _maybe_load_ml()
        if ml is not None:
            try:
                from ...domain.forecast.ml_predictor import build_ml_forecast

                return build_ml_forecast(
                    snap, predictor=ml, horizons=horizons, what_if=False
                )
            except NotEnoughDataError:
                raise
            except Exception:
                # ML упал на конкретном snap — логируем, идём на baseline.
                # Это допустимый сценарий (REQ-12), не ошибка системы.
                _log.exception("ML inference failed, falling back to baseline")

    try:
        return build_forecast(payload)
    except NotEnoughDataError:
        # Это не «упала ML», а реальная нехватка данных — пробрасываем как
        # доменную ошибку для 404.
        raise
    except Exception:  # pragma: no cover — защита от непредвиденного
        _log.exception("baseline inference failed")
        fallback_payload = PredictorInput(
            snapshot=snap, horizons=horizons, override=override, force_baseline=True
        )
        return build_forecast(fallback_payload)


# ---------------------------------------------------------------------------
# Lazy-кэш для ML-предиктора. Прод не платит за загрузку joblib/lightgbm,
# если ML-артефакта нет; единожды загруженная модель остаётся в памяти.
# ---------------------------------------------------------------------------

from functools import lru_cache  # noqa: E402  (намеренно низко: близко к точке использования)


@lru_cache(maxsize=1)
def _maybe_load_ml() -> Any:
    """Возвращает MlPredictor | None. Any в типе — чтобы не тащить условный
    импорт в module-level (lru_cache требует hashable-сигнатуру, что
    forward-ref'ом из ml_predictor задавать неудобно)."""
    try:
        from ...domain.forecast.ml_predictor import load_predictor
    except ImportError:  # pragma: no cover
        return None
    return load_predictor()


def reset_ml_cache() -> None:
    """Сброс lru_cache — вызывается из тестов и админ-команд после
    обновления артефакта."""
    _maybe_load_ml.cache_clear()


# ---------------------------------------------------------------------------
# Восстановление bundle из БД (для кэша и истории)
# ---------------------------------------------------------------------------


def _rows_to_bundle(
    rows: list[InBodyForecast], *, horizons: tuple[int, ...]
) -> ForecastBundle:
    """Собрать ForecastBundle из 3*N строк одного батча."""
    from ...domain.forecast.predictor import (  # локальный импорт ради цикла
        ForecastMetricSeries as _Series,
    )
    from ...domain.forecast.predictor import (
        ForecastPoint as _Point,
    )

    series_map: dict[str, list[_Point]] = {
        "weight_kg": [],
        "body_fat_percent": [],
        "muscle_mass_kg": [],
    }
    confidence = rows[0].confidence
    fallback = rows[0].fallback
    what_if = rows[0].what_if
    model_version = rows[0].model_version
    interpretation = rows[0].interpretation or ""
    for r in rows:
        series_map[r.target_metric].append(
            _Point(
                horizon_weeks=int(r.horizon_weeks),
                point=float(r.point_estimate),
                ci_low=float(r.ci_low),
                ci_high=float(r.ci_high),
            )
        )
    # Фильтр по запрошенным горизонтам — для случая, когда клиент попросил
    # подмножество (например, ?horizons=1,4).
    horizons_set = set(horizons)
    for k, pts in series_map.items():
        series_map[k] = sorted(
            (p for p in pts if p.horizon_weeks in horizons_set),
            key=lambda p: p.horizon_weeks,
        )

    from ...domain.forecast.predictor import ForecastBundle as _Bundle

    return _Bundle(
        confidence=confidence,
        fallback=fallback,
        what_if=what_if,
        model_version=model_version,
        weight_kg=_Series("weight_kg", tuple(series_map["weight_kg"])),
        body_fat_percent=_Series(
            "body_fat_percent", tuple(series_map["body_fat_percent"])
        ),
        muscle_mass_kg=_Series(
            "muscle_mass_kg", tuple(series_map["muscle_mass_kg"])
        ),
        interpretation=interpretation,
    )


# ---------------------------------------------------------------------------
# История прогнозов + автоматическая пристыковка evaluation
# ---------------------------------------------------------------------------


async def list_history(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    limit: int,
    offset: int,
) -> tuple[list[tuple[InBodyForecast, ForecastEvaluation | None]], int]:
    base = select(InBodyForecast).where(InBodyForecast.user_id == user_id)
    total = (
        await session.execute(
            select(func.count(InBodyForecast.id)).where(
                InBodyForecast.user_id == user_id
            )
        )
    ).scalar_one()
    items_stmt = (
        base.order_by(InBodyForecast.generated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = list((await session.execute(items_stmt)).scalars().all())
    # Подгружаем evaluation одним SELECT.
    if rows:
        ids = [r.id for r in rows]
        ev_stmt = select(ForecastEvaluation).where(
            ForecastEvaluation.forecast_id.in_(ids)
        )
        ev_by_forecast = {
            ev.forecast_id: ev
            for ev in (await session.execute(ev_stmt)).scalars().all()
        }
    else:
        ev_by_forecast = {}
    paired = [(r, ev_by_forecast.get(r.id)) for r in rows]
    return paired, int(total)


async def attach_evaluation_for_new_inbody(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    new_inbody: InBodyMeasurement,
    now: datetime | None = None,
) -> int:
    """Найти прогнозы, у которых истёк горизонт ~ measured_at нового InBody,
    и зафиксировать evaluation. Используется триггер-call'ом из inbody-сервиса
    после успешного создания нового замера. Возвращает число привязанных оценок.
    """
    now = now or datetime.now(UTC)
    # Кандидаты: forecast.what_if=False, не имеющий evaluation, чьё
    # generated_at + horizon ≈ new_inbody.measured_at (±3 дня).
    stmt = (
        select(InBodyForecast)
        .where(
            InBodyForecast.user_id == user_id,
            InBodyForecast.what_if.is_(False),
        )
    )
    candidates = list((await session.execute(stmt)).scalars().all())
    if not candidates:
        return 0
    forecast_ids = [c.id for c in candidates]
    existing = {
        ev.forecast_id
        for ev in (
            await session.execute(
                select(ForecastEvaluation).where(
                    ForecastEvaluation.forecast_id.in_(forecast_ids)
                )
            )
        ).scalars().all()
    }

    attached = 0
    for f in candidates:
        if f.id in existing:
            continue
        target_at = f.generated_at + timedelta(weeks=int(f.horizon_weeks))
        if abs((new_inbody.measured_at - target_at).total_seconds()) > (
            EVALUATION_WINDOW.total_seconds()
        ):
            continue
        actual = _actual_for_metric(new_inbody, f.target_metric)
        if actual is None:
            continue
        result = evaluate_forecast(
            point=float(f.point_estimate),
            ci_low=float(f.ci_low),
            ci_high=float(f.ci_high),
            actual=actual,
        )
        session.add(
            ForecastEvaluation(
                forecast_id=f.id,
                actual_inbody_id=new_inbody.id,
                absolute_error=Decimal(str(round(result.absolute_error, 2))),
                within_ci=result.within_ci,
                evaluated_at=now,
            )
        )
        attached += 1
    if attached:
        await session.flush()
    return attached


def _actual_for_metric(m: InBodyMeasurement, metric: str) -> float | None:
    if metric == "weight_kg":
        return float(m.weight_kg)
    if metric == "body_fat_percent":
        return float(m.body_fat_percent)
    if metric == "muscle_mass_kg":
        return float(m.muscle_mass_kg) if m.muscle_mass_kg is not None else None
    return None


async def get_latest_inbody(
    session: AsyncSession, *, user_id: uuid.UUID
) -> InBodyMeasurement | None:
    stmt = (
        select(InBodyMeasurement)
        .where(InBodyMeasurement.user_id == user_id)
        .order_by(InBodyMeasurement.measured_at.desc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_user_goal(
    session: AsyncSession, *, user_id: uuid.UUID
) -> str | None:
    profile = await session.get(UserProfile, user_id)
    return profile.goal if profile else None
