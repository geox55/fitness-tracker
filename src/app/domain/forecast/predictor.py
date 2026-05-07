"""Главный entry point предиктора InBody — `build_forecast`.

Сейчас работает поверх линейного baseline + cold-start. ML-модель будет
подключена через ту же сигнатуру: на вход FeatureSnapshot, на выход
ForecastBundle с `model_version` и `fallback=False`. Если ML-инференс
поднимет исключение, service.py ловит его и зовёт `build_forecast(...,
force_baseline=True)` — REQ-12.

Все функции — pure: detrm. seed, нет I/O, нет БД. Это позволяет тестировать
predictor целиком юнит-тестами (требование тестовой стратегии проекта —
БД-зависимая логика выносится в чистые helpers).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .baseline import LinearFit, linear_fit, linear_forecast, physiological_clip_kg
from .cold_start import cold_start_forecast
from .features import FeatureSnapshot, InBodyPoint
from .interpretation import build_interpretation

# Один источник правды о версии. Бамп при изменении логики baseline-а или
# при появлении ML — service.py пишет это значение в `model_version`.
MODEL_VERSION_BASELINE = "inbody-pred-baseline-0.1.0"

TargetMetric = Literal["weight_kg", "body_fat_percent", "muscle_mass_kg"]
Confidence = Literal["high", "medium", "low"]
DEFAULT_HORIZONS: tuple[int, ...] = (1, 2, 4)


@dataclass(frozen=True)
class Override:
    """What-if переопределения (Scenario 4)."""

    training_frequency: int | None = None
    calories_offset_kcal: int | None = None


@dataclass(frozen=True)
class PredictorInput:
    snapshot: FeatureSnapshot
    horizons: tuple[int, ...] = DEFAULT_HORIZONS
    override: Override | None = None
    force_baseline: bool = False


@dataclass(frozen=True)
class ForecastPoint:
    horizon_weeks: int
    point: float
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class ForecastMetricSeries:
    target_metric: TargetMetric
    points: tuple[ForecastPoint, ...]


@dataclass(frozen=True)
class ForecastBundle:
    confidence: Confidence
    fallback: bool
    what_if: bool
    model_version: str
    weight_kg: ForecastMetricSeries
    body_fat_percent: ForecastMetricSeries
    muscle_mass_kg: ForecastMetricSeries
    interpretation: str
    notes: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------


class NotEnoughDataError(Exception):
    """≥1 InBody — обязательно (REQ-08, ошибка 404)."""


def _series_xs_ys(
    history: tuple[InBodyPoint, ...], pick: str
) -> tuple[list[float], list[float]]:
    """Преобразовать историю в (xs=days_since_first, ys=metric)."""
    base = history[0].measured_at
    xs: list[float] = []
    ys: list[float] = []
    for p in history:
        v = getattr(p, pick)
        if v is None:
            continue
        xs.append((p.measured_at - base).days)
        ys.append(float(v))
    return xs, ys


def _classify_confidence(snap: FeatureSnapshot) -> Confidence:
    """Правила confidence (REQ-04, §10).

    high: ≥4 InBody, ≥8 тренировок за 8 недель, последний InBody ≤14 дней.
    medium: 2-3 InBody, или последний >30 дней; или goal сменился ≤28 дней.
    low: 1 InBody, или последний >60 дней.
    """
    n = len(snap.inbody_history)
    last_age = snap.last_inbody_age_days
    if n == 0:
        return "low"
    if n == 1:
        return "low"
    if last_age is not None and last_age > 60:
        return "low"

    if (
        n >= 4
        and snap.trainings_last_8w >= 8
        and (last_age is not None and last_age <= 14)
    ):
        # Edge case §10: смена цели обнуляет до medium минимум на 4 недели.
        if (
            snap.goal_changed_within_days is not None
            and snap.goal_changed_within_days <= 28
        ):
            return "medium"
        return "high"
    return "medium"


def _apply_override_kg_per_week(
    snap: FeatureSnapshot, override: Override | None
) -> float:
    """Простая поправка для what-if на тренд кг/нед.

    Это не «модель» — это явный rule-based приближение для UX «что если я
    буду тренироваться 5 раз вместо 3» / «если урезать на 200 ккал».
    Используем формулу: 7700 ккал ≈ 1 кг жира.
    """
    if override is None:
        return 0.0
    delta = 0.0
    if override.calories_offset_kcal is not None:
        # Δkcal/day → Δkg/week ≈ Δkcal·7 / 7700
        delta += override.calories_offset_kcal * 7.0 / 7700.0
    if (
        override.training_frequency is not None
        and snap.training_frequency is not None
    ):
        diff = override.training_frequency - snap.training_frequency
        # +1 тренировка/нед ≈ −0.05 кг/нед (грубо: ≈ 350 ккал/тренировка)
        delta -= 0.05 * diff
    return delta


def _clip_for_metric(
    metric: TargetMetric, base: float, point: float, *, horizon_weeks: int
) -> float:
    """Edge case: ограничения скорости изменения (§10)."""
    if metric == "weight_kg":
        return physiological_clip_kg(
            base, point, horizon_weeks=horizon_weeks, max_per_week=1.5
        )
    if metric == "body_fat_percent":
        return physiological_clip_kg(
            base, point, horizon_weeks=horizon_weeks, max_per_week=1.0
        )
    # muscle_mass_kg
    return physiological_clip_kg(
        base, point, horizon_weeks=horizon_weeks, max_per_week=0.5
    )


def _round1(v: float) -> float:
    return round(v, 1)


def _baseline_series(
    snap: FeatureSnapshot,
    *,
    metric: TargetMetric,
    field_name: str,
    horizons: tuple[int, ...],
    extra_kg_per_week: float,
) -> ForecastMetricSeries:
    """OLS по точкам метрики + сдвиг на override + клипинг."""
    history = snap.inbody_history
    base = float(getattr(history[-1], field_name))
    xs, ys = _series_xs_ys(history, field_name)

    fit: LinearFit | None = linear_fit(xs, ys) if len(ys) >= 2 else None

    last_x = (history[-1].measured_at - history[0].measured_at).days
    points: list[ForecastPoint] = []
    for h in horizons:
        target_x = last_x + h * 7
        if fit is None:
            # Один валидный замер по метрике — оставляем плоско.
            point = base
            lo = base
            hi = base
        else:
            point, lo, hi = linear_forecast(fit, target_x)

        # Override применяется только к весу — для жира/мышц у нас слишком
        # грубая физика, чтобы переводить ккал в %. Это явно отмечено в
        # interpretation, см. service.py.
        if metric == "weight_kg":
            point += extra_kg_per_week * h
            lo += extra_kg_per_week * h
            hi += extra_kg_per_week * h

        clipped = _clip_for_metric(metric, base, point, horizon_weeks=h)
        clip_shift = clipped - point
        points.append(
            ForecastPoint(
                horizon_weeks=h,
                point=_round1(clipped),
                ci_low=_round1(lo + clip_shift),
                ci_high=_round1(hi + clip_shift),
            )
        )

    return ForecastMetricSeries(target_metric=metric, points=tuple(points))


def _cold_start_bundle(
    snap: FeatureSnapshot,
    horizons: tuple[int, ...],
    *,
    confidence: Confidence,
    fallback: bool,
    what_if: bool,
) -> ForecastBundle:
    latest = snap.latest
    assert latest is not None  # guaranteed by caller
    raw = cold_start_forecast(
        base_weight_kg=latest.weight_kg,
        base_body_fat_percent=latest.body_fat_percent,
        base_muscle_mass_kg=latest.muscle_mass_kg,
        goal=snap.goal,
        horizons=list(horizons),
    )

    def _series(metric: TargetMetric) -> ForecastMetricSeries:
        return ForecastMetricSeries(
            target_metric=metric,
            points=tuple(
                ForecastPoint(
                    horizon_weeks=p.horizon_weeks,
                    point=_round1(p.point),
                    ci_low=_round1(p.ci_low),
                    ci_high=_round1(p.ci_high),
                )
                for p in raw[metric]
            ),
        )

    weight = _series("weight_kg")
    fat = _series("body_fat_percent")
    muscle = _series("muscle_mass_kg")

    last_h = max(horizons)
    last_w = next(p for p in weight.points if p.horizon_weeks == last_h)
    last_f = next(p for p in fat.points if p.horizon_weeks == last_h)
    last_m = next(p for p in muscle.points if p.horizon_weeks == last_h)

    interp = build_interpretation(
        weight_delta_kg=last_w.point - latest.weight_kg,
        fat_delta_percent=last_f.point - latest.body_fat_percent,
        muscle_delta_kg=last_m.point - (latest.muscle_mass_kg or 0.0),
        horizon_weeks=last_h,
        confidence=confidence,
        fallback=fallback,
    )

    return ForecastBundle(
        confidence=confidence,
        fallback=fallback,
        what_if=what_if,
        model_version=MODEL_VERSION_BASELINE,
        weight_kg=weight,
        body_fat_percent=fat,
        muscle_mass_kg=muscle,
        interpretation=interp,
    )


def build_forecast(payload: PredictorInput) -> ForecastBundle:
    """Главный entry point.

    REQ-08: при <1 InBody — `NotEnoughDataError` (404 в API).
    REQ-07: <4 InBody — cold-start, `confidence: low`.
    REQ-12: при ML-фейле сервис вызывает с force_baseline=True.
    """
    snap = payload.snapshot
    if snap.latest is None:
        raise NotEnoughDataError("at least one InBody measurement is required")

    confidence = _classify_confidence(snap)
    what_if = payload.override is not None

    # Cold start — мало истории для линейной регрессии.
    if len(snap.inbody_history) < 4:
        return _cold_start_bundle(
            snap,
            payload.horizons,
            confidence=confidence,
            fallback=payload.force_baseline,
            what_if=what_if,
        )

    # Достаточно истории — baseline-OLS по каждой метрике.
    extra_kg_per_week = _apply_override_kg_per_week(snap, payload.override)

    weight = _baseline_series(
        snap,
        metric="weight_kg",
        field_name="weight_kg",
        horizons=payload.horizons,
        extra_kg_per_week=extra_kg_per_week,
    )
    fat = _baseline_series(
        snap,
        metric="body_fat_percent",
        field_name="body_fat_percent",
        horizons=payload.horizons,
        extra_kg_per_week=0.0,
    )
    muscle = _baseline_series(
        snap,
        metric="muscle_mass_kg",
        field_name="muscle_mass_kg",
        horizons=payload.horizons,
        extra_kg_per_week=0.0,
    )

    latest = snap.latest
    last_h = max(payload.horizons)
    last_w = next(p for p in weight.points if p.horizon_weeks == last_h)
    last_f = next(p for p in fat.points if p.horizon_weeks == last_h)
    last_m = next(p for p in muscle.points if p.horizon_weeks == last_h)

    interp = build_interpretation(
        weight_delta_kg=last_w.point - latest.weight_kg,
        fat_delta_percent=last_f.point - latest.body_fat_percent,
        muscle_delta_kg=last_m.point - (latest.muscle_mass_kg or 0.0),
        horizon_weeks=last_h,
        confidence=confidence,
        # Когда форсирован baseline (ML упал) — fallback=True; в обычной
        # ветке baseline тоже фактически работает, но для пользователя это
        # «штатный режим» MVP-этапа, поэтому fallback ставим только при
        # явном force_baseline.
        fallback=payload.force_baseline,
    )

    return ForecastBundle(
        confidence=confidence,
        fallback=payload.force_baseline,
        what_if=what_if,
        model_version=MODEL_VERSION_BASELINE,
        weight_kg=weight,
        body_fat_percent=fat,
        muscle_mass_kg=muscle,
        interpretation=interp,
    )
