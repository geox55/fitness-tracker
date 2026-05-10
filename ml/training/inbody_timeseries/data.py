"""Чтение Dataset-B + feature engineering.

Pipeline:
    csv  → pandas.DataFrame
         → make_features_targets:
             X = [age, sex_male, height_cm, weight_kg, body_fat_percent,
                  muscle_mass_kg, bmi, ffm, training_volume_t, calories_t,
                  goal_weight_loss, goal_muscle_gain]
             y = {Δweight, Δbf, Δmm}    # дельты до t+1
         → split по колонке `split` ∈ {train, val, test}

Дельты вместо абсолютных таргетов — стандартный приём для time-series при
малых выборках: модель учится «куда идёт траектория», а не повторять текущее
значение (что предсказали бы любые слабые признаки → утечка persistence).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

# Колонки фичей в фиксированном порядке: важно, чтобы train/predict шли по
# одной и той же сигнатуре. Хранится в manifest рядом с моделью.
FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    "age",
    "sex_male",
    "height_cm",
    "weight_kg",
    "body_fat_percent",
    "muscle_mass_kg",
    "bmi",
    "ffm",
    "training_volume_t",
    "calories_t",
    "goal_weight_loss",
    "goal_muscle_gain",
)

# Таргеты: дельты по 3 метрикам InBody. Ключ — то, что модель предсказывает,
# значение — пара (anchor_col, label_col) для расчёта дельты из датасета.
PREDICT_TARGETS: Final[dict[str, tuple[str, str]]] = {
    "delta_weight_kg": ("weight_kg", "target_weight_t1"),
    "delta_body_fat_percent": ("body_fat_percent", "target_bf_t1"),
    "delta_muscle_mass_kg": ("muscle_mass_kg", "target_mm_t1"),
}


@dataclass(frozen=True)
class DatasetSplit:
    """Один сплит — три параллельных фрейма (X, y, group).

    `group` — anon_user_id, нужен для group-aware CV: при cross-validation
    нельзя смешивать недели одного пользователя между fold'ами.
    """

    X: pd.DataFrame
    y: pd.DataFrame  # колонки = ключи из PREDICT_TARGETS
    group: pd.Series  # anon_user_id


def load_dataset_b(csv_path: Path) -> pd.DataFrame:
    """Прочитать `dataset_b_inbody_timeseries.csv` целиком.

    Минимальная валидация колонок — чтобы пайплайн не падал на половине.
    Типы приводим явно: pandas умеет угадать неправильно (особенно sex как
    object вместо категории).
    """
    df = pd.read_csv(csv_path)
    required = {
        "anon_user_id",
        "t_week",
        "age",
        "sex",
        "height_cm",
        "weight_kg",
        "body_fat_percent",
        "muscle_mass_kg",
        "training_volume_t",
        "calories_t",
        "target_weight_t1",
        "target_bf_t1",
        "target_mm_t1",
        "split",
        "is_synthetic",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"dataset is missing columns: {sorted(missing)}; got {list(df.columns)}"
        )
    return df


def _infer_goal_column(df: pd.DataFrame) -> pd.Series:
    """Spec 012 не пишет `goal` явной колонкой — выводим её из траектории.

    Эвристика: смотрим знак средней Δweight по пользователю (target_weight_t1
    − weight_kg). <−0.05 кг/нед → weight_loss, >+0.05 → muscle_gain, иначе
    maintenance. Это совпадает с медианными дельтами в `synthesize.py`
    (_GOAL_DELTA), что согласует ETL и training.

    Возвращаем категориальный Series с теми же значениями, что в profile.goal.
    """
    delta = df["target_weight_t1"] - df["weight_kg"]
    per_user_mean = delta.groupby(df["anon_user_id"]).transform("mean")
    goal = pd.Series(
        np.where(
            per_user_mean < -0.05,
            "weight_loss",
            np.where(per_user_mean > 0.05, "muscle_gain", "maintenance"),
        ),
        index=df.index,
        name="goal",
    )
    return goal


def make_features_targets(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """`df` → (X, y, group). Используется и train, и evaluate.

    Несколько вычисляемых фичей:
    - `bmi = weight / (height/100)^2` — ровно та формула, что в backend;
    - `ffm = weight · (1 − bf/100)` — fat-free mass, синхронно с
      `synthesize.py._initial_muscle_mass`;
    - `sex_male` — one-hot (sex принимает male/female в spec 012);
    - `goal_*` — one-hot для weight_loss / muscle_gain (maintenance = baseline).

    `muscle_mass_kg` может быть NaN — допустимо: LightGBM умеет работать
    с пропусками нативно, для Ridge мы его imputим медианой по train в
    train_*.py.
    """
    height_m = df["height_cm"] / 100.0
    bmi = df["weight_kg"] / (height_m**2)
    ffm = df["weight_kg"] * (1.0 - df["body_fat_percent"] / 100.0)

    goal = _infer_goal_column(df)

    X = pd.DataFrame(
        {
            "age": df["age"].astype(float),
            "sex_male": (df["sex"] == "male").astype(int),
            "height_cm": df["height_cm"].astype(float),
            "weight_kg": df["weight_kg"].astype(float),
            "body_fat_percent": df["body_fat_percent"].astype(float),
            "muscle_mass_kg": df["muscle_mass_kg"].astype(float),
            "bmi": bmi.astype(float),
            "ffm": ffm.astype(float),
            "training_volume_t": df["training_volume_t"].astype(float),
            "calories_t": df["calories_t"].astype(float),
            "goal_weight_loss": (goal == "weight_loss").astype(int),
            "goal_muscle_gain": (goal == "muscle_gain").astype(int),
        }
    )

    y = pd.DataFrame(
        {
            "delta_weight_kg": df["target_weight_t1"] - df["weight_kg"],
            "delta_body_fat_percent": df["target_bf_t1"] - df["body_fat_percent"],
            "delta_muscle_mass_kg": df["target_mm_t1"] - df["muscle_mass_kg"],
        }
    )

    return X, y, df["anon_user_id"]


def split_dataset(df: pd.DataFrame) -> dict[str, DatasetSplit]:
    """Разрезать датасет по колонке `split` на train/val/test.

    No-leakage гарантируется ETL'ом — anon_user_id целиком уходит в один
    из сплитов; здесь мы только фильтруем и считаем фичи.
    """
    out: dict[str, DatasetSplit] = {}
    for split_name in ("train", "val", "test"):
        sub = df[df["split"] == split_name].copy()
        X, y, group = make_features_targets(sub)
        out[split_name] = DatasetSplit(X=X, y=y, group=group)
    return out
