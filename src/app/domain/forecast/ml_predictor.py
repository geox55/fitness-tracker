"""ML-инференс InBody-предиктора (spec 008, целевая модель из дипломной работы).

Загружает артефакт LightGBM quantile-модели, обученной в
`ml/training/inbody_timeseries/`. Прод-API не зависит от lightgbm/joblib
на старте — импорты ленивые, и если артефакта нет (или зависимости не
установлены), `MaybeMlPredictor.load()` вернёт None, а `predictor.build_forecast`
останется на baseline (REQ-12).

Алгоритм инференса (рекурсивный one-step):
    state ← latest InBody
    for h in (1, 2, 4):
        Δ_q10, Δ_q50, Δ_q90 = model.predict_step(features(state))
        state ← state + Δ_q50           # точечная оценка идёт дальше
        ci ← state + (Δ_q10, Δ_q90)     # CI считаем относительно той же state
        save point (h, state, ci_low, ci_high)

Этот подход совпадает с обучающей задачей (модель училась next-week-Δ);
для горизонта 4 недели мы повторяем step 4 раза, накапливая ошибку — это
ожидаемое поведение, проверяется в evaluate.py через рекурсивную метрику
(out of scope первого прохода: сейчас offline-метрики считаются на one-step).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .features import FeatureSnapshot
from .predictor import (
    DEFAULT_HORIZONS,
    ForecastBundle,
    ForecastMetricSeries,
    ForecastPoint,
    TargetMetric,
    _classify_confidence,
    _round1,
)

if TYPE_CHECKING:  # pragma: no cover
    pass

# Путь к каталогу с артефактами. Конкретная версия выбирается в
# `_pick_latest_version`; при необходимости можно зафиксировать через
# env-переменную INBODY_ML_VERSION (см. config.py при будущем подключении).
DEFAULT_MODELS_ROOT = Path("ml/models/inbody_pred/lgbm")

# Маппинг target_metric → имя файла target в датасете обучения.
_TARGET_DELTAS: dict[TargetMetric, str] = {
    "weight_kg": "delta_weight_kg",
    "body_fat_percent": "delta_body_fat_percent",
    "muscle_mass_kg": "delta_muscle_mass_kg",
}


@dataclass(frozen=True)
class _LoadedQuantiles:
    """3 booster'а одного target: q=0.1, 0.5, 0.9."""

    q10: object  # lgb.Booster, но не импортируем тип на верхнем уровне
    q50: object
    q90: object


@dataclass(frozen=True)
class MlPredictor:
    """Загруженная модель + порядок фичей (для безопасной сериализации snap → X)."""

    feature_columns: tuple[str, ...]
    quantiles: dict[TargetMetric, _LoadedQuantiles]
    model_version: str


def _pick_latest_version(models_root: Path) -> Path | None:
    """Найти самый новый каталог `vX.Y.Z`. Простая лексикографическая сортировка
    хватает, пока версии семвер-совместимы (нули в minor/patch не пропускаем).
    """
    if not models_root.exists():
        return None
    versions = sorted(p for p in models_root.iterdir() if p.is_dir() and p.name.startswith("v"))
    return versions[-1] if versions else None


def _read_manifest(model_dir: Path) -> dict[str, Any] | None:
    manifest_path = model_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    data: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    return data


def _load_quantile_models(
    *,
    model_dir: Path,
    targets: tuple[str, ...],
) -> dict[TargetMetric, _LoadedQuantiles] | None:
    """Загрузить 3 файла на каждый target. Возвращает None при любой проблеме —
    вызывающий код сделает fallback к baseline.

    joblib импортируется лениво: ML-зависимости — отдельная группа (см.
    pyproject.toml `dependency-groups.ml`), и при их отсутствии прод-API
    должен спокойно стартовать.
    """
    try:  # pragma: no cover (зависит от окружения)
        import joblib
    except ImportError:
        return None

    out: dict[TargetMetric, _LoadedQuantiles] = {}
    for delta_name in targets:
        # delta_weight_kg → weight_kg, и т.д. — обратное к _TARGET_DELTAS.
        target_metric = next(
            (k for k, v in _TARGET_DELTAS.items() if v == delta_name),
            None,
        )
        if target_metric is None:
            return None
        try:
            q10 = joblib.load(model_dir / f"{delta_name}_q10.joblib")
            q50 = joblib.load(model_dir / f"{delta_name}_q50.joblib")
            q90 = joblib.load(model_dir / f"{delta_name}_q90.joblib")
        except (FileNotFoundError, OSError):
            return None
        out[target_metric] = _LoadedQuantiles(q10=q10, q50=q50, q90=q90)
    return out


def load_predictor(models_root: Path = DEFAULT_MODELS_ROOT) -> MlPredictor | None:
    """Главная фабрика: ищет последнюю версию, читает manifest, грузит модели.

    None означает «ML недоступен» — это ожидаемое состояние в окружениях
    без обученной модели; сервис тогда просто остаётся на baseline.
    """
    model_dir = _pick_latest_version(models_root)
    if model_dir is None:
        return None
    manifest = _read_manifest(model_dir)
    if manifest is None:
        return None
    if not manifest.get("has_quantiles"):
        # MlPredictor спроектирован под quantile-модели (нужны CI-bands);
        # ridge/persistence сюда не подходят, оставляем baseline.
        return None
    feature_columns = tuple(manifest["feature_columns"])
    quantiles = _load_quantile_models(
        model_dir=model_dir,
        targets=tuple(manifest["targets"]),
    )
    if quantiles is None:
        return None
    return MlPredictor(
        feature_columns=feature_columns,
        quantiles=quantiles,
        model_version=manifest["model_version"],
    )


# ---------------------------------------------------------------------------
# Feature engineering: snapshot → row фичей в порядке feature_columns
# ---------------------------------------------------------------------------


def _features_row(
    snap: FeatureSnapshot,
    *,
    state_weight_kg: float,
    state_body_fat_percent: float,
    state_muscle_mass_kg: float | None,
    feature_columns: tuple[str, ...],
) -> list[float]:
    """Собрать фичи в **строгом** порядке feature_columns из manifest'а.

    `state_*` приходит из текущего шага рекурсии: на h=1 это последний
    InBody, на h>1 — обновлённое состояние. Фичи рассчитываются по той
    же логике, что в `ml.training.inbody_timeseries.data.make_features_targets`,
    чтобы train/serve были sync.
    """
    height = snap.height_cm or 175.0  # fallback: средний; при пустом профиле
    age = snap.age_years if snap.age_years is not None else 30
    sex_male = 1 if snap.sex == "male" else 0
    bmi = state_weight_kg / ((height / 100.0) ** 2)
    ffm = state_weight_kg * (1.0 - state_body_fat_percent / 100.0)
    muscle = state_muscle_mass_kg if state_muscle_mass_kg is not None else float("nan")

    # tonnage->частота: грубая оценка как «trainings_last_8w / 8».
    # Для one-step предсказания недельная частота — натуральная фича.
    training_volume = snap.trainings_last_8w / 8.0
    # calories_t — берём BMR·1.5 если actual_calories известен; иначе грубо.
    calories = float(snap.actual_calories_kcal or snap.target_calories_kcal or 2400.0)
    goal_wl = 1 if snap.goal == "weight_loss" else 0
    goal_mg = 1 if snap.goal == "muscle_gain" else 0

    raw = {
        "age": float(age),
        "sex_male": float(sex_male),
        "height_cm": float(height),
        "weight_kg": float(state_weight_kg),
        "body_fat_percent": float(state_body_fat_percent),
        "muscle_mass_kg": float(muscle),
        "bmi": float(bmi),
        "ffm": float(ffm),
        "training_volume_t": float(training_volume),
        "calories_t": calories,
        "goal_weight_loss": float(goal_wl),
        "goal_muscle_gain": float(goal_mg),
    }
    # Берём именно в порядке feature_columns: даже если manifest когда-то
    # переставит/добавит фичу, train и serve остаются синхронными.
    return [raw[col] for col in feature_columns]


# ---------------------------------------------------------------------------
# Рекурсивный one-step → multi-horizon
# ---------------------------------------------------------------------------


def _predict_step(
    *,
    booster: object,
    feats: list[float],
) -> float:
    """Одна предсказательная точка. lgb.Booster.predict хочет 2D, отдаёт array."""
    # Импорт numpy локально — модуль не должен тащить numpy в прод без ML.
    import numpy as np  # pragma: no cover

    arr = np.asarray([feats], dtype=float)
    pred = booster.predict(arr)  # type: ignore[attr-defined]
    return float(pred[0])


def _clip_for_metric(metric: TargetMetric, base: float, point: float, *, h: int) -> float:
    """Те же физиологические границы, что и в baseline (см. predictor.py)."""
    from .baseline import physiological_clip_kg

    if metric == "weight_kg":
        return physiological_clip_kg(base, point, horizon_weeks=h, max_per_week=1.5)
    if metric == "body_fat_percent":
        return physiological_clip_kg(base, point, horizon_weeks=h, max_per_week=1.0)
    return physiological_clip_kg(base, point, horizon_weeks=h, max_per_week=0.5)


def build_ml_forecast(
    snap: FeatureSnapshot,
    *,
    predictor: MlPredictor,
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    what_if: bool = False,
) -> ForecastBundle:
    """Multi-horizon прогноз: рекурсивно применяем one-step-модель.

    Caller должен убедиться, что у snap есть latest и достаточно истории.
    Здесь ничего не рассчитываем «на флайт» — только предсказываем.
    """
    latest = snap.latest
    if latest is None:
        # Должно отлавливаться вызывающим кодом, но защитимся.
        raise ValueError("ML predictor needs at least one InBody point")

    base_w = float(latest.weight_kg)
    base_f = float(latest.body_fat_percent)
    base_m = float(latest.muscle_mass_kg) if latest.muscle_mass_kg is not None else 0.0

    # Текущее «состояние» на каждом шаге рекурсии.
    state_w = base_w
    state_f = base_f
    state_m: float | None = (
        float(latest.muscle_mass_kg) if latest.muscle_mass_kg is not None else None
    )

    # Накопленные дельты для CI: складываем нижние/верхние квантили.
    cum_lo: dict[TargetMetric, float] = {
        "weight_kg": 0.0,
        "body_fat_percent": 0.0,
        "muscle_mass_kg": 0.0,
    }
    cum_hi: dict[TargetMetric, float] = {
        "weight_kg": 0.0,
        "body_fat_percent": 0.0,
        "muscle_mass_kg": 0.0,
    }

    points: dict[TargetMetric, list[ForecastPoint]] = {
        "weight_kg": [],
        "body_fat_percent": [],
        "muscle_mass_kg": [],
    }
    metrics_iter: tuple[TargetMetric, ...] = (
        "weight_kg",
        "body_fat_percent",
        "muscle_mass_kg",
    )

    sorted_h = sorted(set(horizons))
    prev_h = 0
    for h in sorted_h:
        # Сколько недель шагнуть от prev_h до h. Обычно h=1,2,4 → шаги 1,1,2.
        steps = h - prev_h
        for _ in range(steps):
            feats = _features_row(
                snap,
                state_weight_kg=state_w,
                state_body_fat_percent=state_f,
                state_muscle_mass_kg=state_m,
                feature_columns=predictor.feature_columns,
            )
            for metric in metrics_iter:
                booster = predictor.quantiles[metric]
                d_lo = _predict_step(booster=booster.q10, feats=feats)
                d_md = _predict_step(booster=booster.q50, feats=feats)
                d_hi = _predict_step(booster=booster.q90, feats=feats)

                # Точечное состояние шагает по медиане; CI — кумулятивное по q10/q90.
                if metric == "weight_kg":
                    state_w += d_md
                elif metric == "body_fat_percent":
                    state_f += d_md
                else:
                    if state_m is not None:
                        state_m += d_md
                cum_lo[metric] += d_lo
                cum_hi[metric] += d_hi

        prev_h = h

        # Зафиксировали состояние на этом горизонте.
        for metric in ("weight_kg", "body_fat_percent", "muscle_mass_kg"):
            if metric == "weight_kg":
                point = state_w
                base = base_w
            elif metric == "body_fat_percent":
                point = state_f
                base = base_f
            else:
                if state_m is None:
                    # У latest не было muscle_mass_kg — отдаём «плоско», как baseline.
                    points["muscle_mass_kg"].append(
                        ForecastPoint(
                            horizon_weeks=h,
                            point=_round1(base_m),
                            ci_low=_round1(base_m),
                            ci_high=_round1(base_m),
                        )
                    )
                    continue
                point = state_m
                base = base_m
            clipped = _clip_for_metric(metric, base, point, h=h)
            shift = clipped - point
            ci_lo = base + cum_lo[metric] + shift
            ci_hi = base + cum_hi[metric] + shift
            points[metric].append(
                ForecastPoint(
                    horizon_weeks=h,
                    point=_round1(clipped),
                    ci_low=_round1(ci_lo),
                    ci_high=_round1(ci_hi),
                )
            )

    confidence = _classify_confidence(snap)
    # Интерпретация подхватится из predictor.build_interpretation в caller'е,
    # либо заполним лаконичную здесь:
    from .interpretation import build_interpretation

    last_h = max(sorted_h)
    last_w = next(p for p in points["weight_kg"] if p.horizon_weeks == last_h)
    last_f = next(p for p in points["body_fat_percent"] if p.horizon_weeks == last_h)
    last_m = next(p for p in points["muscle_mass_kg"] if p.horizon_weeks == last_h)
    interp = build_interpretation(
        weight_delta_kg=last_w.point - base_w,
        fat_delta_percent=last_f.point - base_f,
        muscle_delta_kg=last_m.point - base_m,
        horizon_weeks=last_h,
        confidence=confidence,
        fallback=False,
    )

    def _series(metric: TargetMetric) -> ForecastMetricSeries:
        return ForecastMetricSeries(target_metric=metric, points=tuple(points[metric]))

    return ForecastBundle(
        confidence=confidence,
        fallback=False,
        what_if=what_if,
        model_version=predictor.model_version,
        weight_kg=_series("weight_kg"),
        body_fat_percent=_series("body_fat_percent"),
        muscle_mass_kg=_series("muscle_mass_kg"),
        interpretation=interp,
    )
