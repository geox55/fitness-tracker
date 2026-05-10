"""Чтение Dataset-C + feature engineering для рекомендатора.

Pipeline:
    csv → pandas.DataFrame
        → make_features_targets:
            X = [user_*, exercise_*, one-hot goal/level/primary_muscle_group/body_region]
            y = label (0/1)
        → split по колонке `split`

Дизайн фичей:
- Числовые user-фичи (age, bmi, ffm) — как есть, LGBM сам найдёт сплиты;
- One-hot для категорий (goal, level, primary_muscle_group, body_region) —
  у LGBM есть нативная поддержка categorical, но one-hot переносим в LR-baseline;
- Equipment-bools (needs_*) — уже в датасете;
- `is_advanced` — бинарный признак уровня сложности;
- Парные фичи (compatibility) считаем тут же: совпадает ли target group
  с приоритетной для goal'а — это снимает с модели burden угадывать
  rule-based heuristic, и оставляет ей искать subtle patterns поверх.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

# Числовые фичи пользователя (для модели — без масштабирования; LGBM
# инвариантен к монотонной трансформации). LR-baseline сам нормирует.
USER_FEATURES: Final[tuple[str, ...]] = (
    "user_age",
    "user_sex_male",
    "user_height_cm",
    "user_weight_kg",
    "user_body_fat",
    "user_bmi",
    "user_ffm",
    "user_equipment_count",
)

# Фичи упражнения. needs_* и is_advanced попадают сюда напрямую,
# muscle_group/region — через one-hot (см. _add_categorical).
EXERCISE_FEATURES: Final[tuple[str, ...]] = (
    "is_advanced",
    "needs_barbell",
    "needs_dumbbell",
    "needs_machine",
    "needs_bodyweight_only",
)

# Допустимые значения для one-hot. Фиксируем явно, чтобы train/serve
# совпадали по столбцам, даже если в test-сплите какая-то категория не
# встретилась (одно user_goal на 1000 строк может оказаться вне фрейма).
_GOAL_VALUES = ("weight_loss", "muscle_gain", "maintenance")
_LEVEL_VALUES = ("beginner", "intermediate", "advanced")
_GROUPS = (
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
_REGIONS = ("upper", "lower", "core")


@dataclass(frozen=True)
class DatasetSplit:
    X: pd.DataFrame
    y: pd.Series
    group: pd.Series  # anon_user_id — для group-aware CV


def load_dataset_c(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = {
        "anon_user_id",
        "user_age",
        "user_sex_male",
        "user_height_cm",
        "user_weight_kg",
        "user_body_fat",
        "user_goal",
        "user_level",
        "user_equipment_count",
        "exercise_id",
        "primary_muscle_group",
        "body_region",
        "is_advanced",
        "needs_barbell",
        "needs_dumbbell",
        "needs_machine",
        "needs_bodyweight_only",
        "label",
        "split",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"dataset is missing columns: {sorted(missing)}")
    return df


def _onehot(series: pd.Series, values: tuple[str, ...], prefix: str) -> pd.DataFrame:
    """Жёсткий one-hot по фиксированному словарю значений. Если в данных
    проскочила категория не из values — у этой строки все колонки = 0
    (а не падение). Это устойчиво для serving'а."""
    return pd.DataFrame(
        {f"{prefix}_{v}": (series == v).astype(int) for v in values},
        index=series.index,
    )


def make_features_targets(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """`df` → (X, y, group). Используется и train, и serve (для одной строки)."""
    bmi = df["user_weight_kg"] / ((df["user_height_cm"] / 100.0) ** 2)
    ffm = df["user_weight_kg"] * (1.0 - df["user_body_fat"] / 100.0)

    X = pd.DataFrame(
        {
            "user_age": df["user_age"].astype(float),
            "user_sex_male": df["user_sex_male"].astype(int),
            "user_height_cm": df["user_height_cm"].astype(float),
            "user_weight_kg": df["user_weight_kg"].astype(float),
            "user_body_fat": df["user_body_fat"].astype(float),
            "user_bmi": bmi.astype(float),
            "user_ffm": ffm.astype(float),
            "user_equipment_count": df["user_equipment_count"].astype(int),
            "is_advanced": df["is_advanced"].astype(int),
            "needs_barbell": df["needs_barbell"].astype(int),
            "needs_dumbbell": df["needs_dumbbell"].astype(int),
            "needs_machine": df["needs_machine"].astype(int),
            "needs_bodyweight_only": df["needs_bodyweight_only"].astype(int),
        }
    )

    X = pd.concat(
        [
            X,
            _onehot(df["user_goal"], _GOAL_VALUES, "goal"),
            _onehot(df["user_level"], _LEVEL_VALUES, "level"),
            _onehot(df["primary_muscle_group"], _GROUPS, "group"),
            _onehot(df["body_region"], _REGIONS, "region"),
        ],
        axis=1,
    )

    return X, df["label"].astype(int), df["anon_user_id"]


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Возвращает имена колонок X в фиксированном порядке. Используется
    в manifest, чтобы serving собрал фичи в той же сигнатуре, в какой
    обучалась модель."""
    X, _, _ = make_features_targets(df.head(1))
    return list(X.columns)


def split_dataset(df: pd.DataFrame) -> dict[str, DatasetSplit]:
    out: dict[str, DatasetSplit] = {}
    for split_name in ("train", "val", "test"):
        sub = df[df["split"] == split_name]
        X, y, g = make_features_targets(sub)
        out[split_name] = DatasetSplit(X=X, y=y, group=g)
    return out


def positives_ratio(df: pd.DataFrame) -> float:
    """Доля positives в датасете — для понимания, насколько imbalance'ный."""
    if df.empty:
        return 0.0
    return float(np.mean(df["label"] == 1))
