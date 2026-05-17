"""ML-инференс workout-рекомендатора — гибридная схема spec 006 §2.

Загружает LightGBM-артефакт из `ml/models/workout_rec/lgbm/v*/` и выдаёт
скор релевантности для пары (user, exercise). Прод-API стартует без
ML-зависимостей: `load_ranker()` возвращает None при отсутствии
артефакта/joblib — composer тогда выбирает упражнения rule-based
(REQ-16 fallback).

Архитектура совпадает с InBody-предиктором (`forecast/ml_predictor.py`):
- lazy-load, ленивый импорт joblib/lightgbm/numpy;
- порядок фичей читается из `manifest.feature_columns`, чтобы train/serve
  не разъезжались при добавлении/перестановке колонок;
- эвристика `is_advanced` дублируется из ETL (`ml/etl/workout_recommender/
  labelling.py`) — это намеренная копия: прод-код не тянет ETL-стек.

Контракт `score_exercises`: возвращает `dict[exercise_id, score ∈ [0,1]]`
батчем. На каталоге ~900 строк × 36 фичей один батч проходит за <50 мс
на CPU; чанкование не требуется.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MODELS_ROOT = Path("ml/models/workout_rec/lgbm")

# Те же словари, что в ml/training/workout_recommender/data.py — критично
# держать в одном порядке с feature_columns, иначе serve выдаст мусор.
_GOAL_VALUES: tuple[str, ...] = ("weight_loss", "muscle_gain", "maintenance")
_LEVEL_VALUES: tuple[str, ...] = ("beginner", "intermediate", "advanced")
_GROUPS: tuple[str, ...] = (
    "abs",
    "back",
    "biceps",
    "calves",
    "chest",
    "forearms",
    "glutes",
    "hamstrings",
    "lats",
    "lower_back",
    "quads",
    "shoulders",
    "traps",
    "triceps",
)
_REGIONS: tuple[str, ...] = ("upper", "lower", "core")

# Копия из ml/etl/workout_recommender/labelling.py::ADVANCED_KEYWORDS.
# Дублируем, чтобы прод не импортировал ETL-модуль (там pandas/numpy
# на верхнем уровне).
_ADVANCED_KEYWORDS: tuple[str, ...] = (
    "snatch",
    "clean",
    "jerk",
    "muscle_up",
    "muscle-up",
    "pistol",
    "handstand",
    "front_squat",
    "overhead_squat",
    "good_morning",
    "deadlift",
)


@dataclass(frozen=True)
class MlRanker:
    """Загруженный артефакт + порядок фичей из manifest'а."""

    feature_columns: tuple[str, ...]
    booster: Any  # lightgbm.Booster, но не импортируем тип на верхнем уровне
    model_version: str


@dataclass(frozen=True)
class RankerUserFeatures:
    """User-часть фичей для одного скоринга. Поля совпадают с обучающими
    колонками Dataset-C (см. `ml/training/workout_recommender/data.py`).
    """

    age: int
    sex_male: int
    height_cm: float
    weight_kg: float
    body_fat_percent: float
    equipment_count: int
    goal: str  # weight_loss | muscle_gain | maintenance
    level: str  # beginner | intermediate | advanced


@dataclass(frozen=True)
class RankerExerciseFeatures:
    """Exercise-часть фичей. Принимаем сырые поля каталога, computed-фичу
    `is_advanced` восстанавливаем здесь же — это эвристика по name/id,
    которая в БД не хранится.
    """

    exercise_id: str
    primary_muscle_group: str
    body_region: str
    equipment: tuple[str, ...]
    name: str = ""


def _pick_latest_version(root: Path) -> Path | None:
    """Лексикографический выбор: vX.Y.Z с самым большим именем. Хватит,
    пока версии семвер-совместимые без leading zeros в minor/patch."""
    if not root.exists():
        return None
    versions = sorted(
        p for p in root.iterdir() if p.is_dir() and p.name.startswith("v")
    )
    return versions[-1] if versions else None


def load_ranker(models_root: Path = DEFAULT_MODELS_ROOT) -> MlRanker | None:
    """Главная фабрика. None означает «ML недоступен» — это нормальный
    режим: прод-API без артефакта работает на rule-based composer.
    """
    model_dir = _pick_latest_version(models_root)
    if model_dir is None:
        return None
    manifest_path = model_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest: dict[str, Any] = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return None

    feature_columns = tuple(manifest.get("feature_columns", ()))
    if not feature_columns:
        return None

    try:  # pragma: no cover — зависит от окружения
        import joblib
    except ImportError:
        return None
    artifact = model_dir / "lgbm.joblib"
    if not artifact.exists():
        return None
    try:
        booster = joblib.load(artifact)
    except (OSError, ValueError):
        return None

    return MlRanker(
        feature_columns=feature_columns,
        booster=booster,
        model_version=str(manifest.get("model_version", "workout-rec-lgbm")),
    )


def _is_likely_advanced(exercise_id: str, name: str) -> bool:
    """Эвристика «вероятно advanced» — копия из ETL labelling.py."""
    lower = (exercise_id + " " + name).lower()
    return any(k in lower for k in _ADVANCED_KEYWORDS)


def _build_features(
    user: RankerUserFeatures,
    ex: RankerExerciseFeatures,
    feature_columns: tuple[str, ...],
) -> list[float]:
    """Собрать строку фичей в порядке `feature_columns`.

    Зеркало `ml/training/workout_recommender/data.py::make_features_targets`:
    одни и те же числовые/one-hot колонки. Любая неизвестная колонка из
    feature_columns получит 0.0 (forward-compat: если manifest когда-то
    добавит новую фичу, serve не упадёт, просто отдаст 0.0).
    """
    bmi = user.weight_kg / ((user.height_cm / 100.0) ** 2)
    ffm = user.weight_kg * (1.0 - user.body_fat_percent / 100.0)
    needs_bodyweight_only = 1 if set(ex.equipment) <= {"bodyweight"} else 0

    raw: dict[str, float] = {
        "user_age": float(user.age),
        "user_sex_male": float(user.sex_male),
        "user_height_cm": float(user.height_cm),
        "user_weight_kg": float(user.weight_kg),
        "user_body_fat": float(user.body_fat_percent),
        "user_bmi": float(bmi),
        "user_ffm": float(ffm),
        "user_equipment_count": float(user.equipment_count),
        "is_advanced": float(_is_likely_advanced(ex.exercise_id, ex.name)),
        "needs_barbell": float("barbell" in ex.equipment),
        "needs_dumbbell": float("dumbbell" in ex.equipment),
        "needs_machine": float("machine" in ex.equipment),
        "needs_bodyweight_only": float(needs_bodyweight_only),
    }
    for v in _GOAL_VALUES:
        raw[f"goal_{v}"] = 1.0 if user.goal == v else 0.0
    for v in _LEVEL_VALUES:
        raw[f"level_{v}"] = 1.0 if user.level == v else 0.0
    for v in _GROUPS:
        raw[f"group_{v}"] = 1.0 if ex.primary_muscle_group == v else 0.0
    for v in _REGIONS:
        raw[f"region_{v}"] = 1.0 if ex.body_region == v else 0.0

    return [raw.get(col, 0.0) for col in feature_columns]


def score_exercises(
    ranker: MlRanker,
    *,
    user: RankerUserFeatures,
    exercises: list[RankerExerciseFeatures],
) -> dict[str, float]:
    """Батчевый predict — одна матрица на весь пул.

    `lgb.Booster.predict(X)` для objective='binary' возвращает уже
    вероятности (а не logits). На пустом списке — `{}`, чтобы вызывающий
    мог безопасно дёргать без проверки.
    """
    if not exercises:
        return {}
    import numpy as np  # ленивый импорт: numpy не должен тянуться в прод без ML

    feats = np.asarray(
        [_build_features(user, ex, ranker.feature_columns) for ex in exercises],
        dtype=float,
    )
    booster = ranker.booster
    # train_lgbm.py сохраняет raw lgb.Booster; на всякий случай оставляем
    # ветку sklearn-обёртки, если артефакт когда-нибудь пересохранят
    # через LGBMClassifier.
    if hasattr(booster, "predict_proba"):
        probs = booster.predict_proba(feats)[:, 1]
    else:
        probs = booster.predict(feats)
    return {ex.exercise_id: float(p) for ex, p in zip(exercises, probs, strict=False)}


__all__ = [
    "MlRanker",
    "RankerExerciseFeatures",
    "RankerUserFeatures",
    "load_ranker",
    "score_exercises",
]
