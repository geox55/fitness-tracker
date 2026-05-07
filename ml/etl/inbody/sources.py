"""Парсеры raw CSV S3/S4 → `Anchor`.

Читаем через стандартный `csv` модуль, чтобы пайплайн не требовал pandas.
Колонки реальных Kaggle-файлов мапятся в общий формат явным словарём —
если автор датасета переименует колонку, фейлится только парсер, остальной
pipeline не трогается.

Имена колонок в S3 и S4 зафиксированы по состоянию на момент написания спеки;
в проектной ветке Маши они привязаны к sha256-хешу файла (REQ-20).
"""

from __future__ import annotations

import csv
from pathlib import Path

from .anchor import Anchor

# ---------- S3: gym-members-exercise-dataset --------------------------------
# Kaggle URL: https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset
# Колонки реального файла: Age, Gender, Weight (kg), Height (m),
# Max_BPM, Avg_BPM, Resting_BPM, Session_Duration (hours),
# Calories_Burned, Workout_Type, Fat_Percentage, Water_Intake (liters),
# Workout_Frequency (days/week), Experience_Level, BMI

_S3_GENDER_MAP = {"male": "male", "female": "female", "m": "male", "f": "female"}
_S3_LEVEL_MAP = {"1": "beginner", "2": "intermediate", "3": "advanced"}


def _f(row: dict[str, str], key: str) -> float | None:
    raw = row.get(key)
    if raw is None or raw == "" or raw.lower() == "nan":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _i(row: dict[str, str], key: str) -> int | None:
    f = _f(row, key)
    return int(f) if f is not None else None


def parse_s3_csv(path: Path) -> list[Anchor]:
    """Распарсить gym-members-exercise-dataset.csv в список Anchor.

    Строки без обязательных полей (sex, age, height, weight, body_fat) —
    отбрасываются: дальше impute.is_outlier их всё равно отрежет.
    """
    anchors: list[Anchor] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            sex_raw = (row.get("Gender") or "").strip().lower()
            sex = _S3_GENDER_MAP.get(sex_raw)
            if sex is None:
                continue
            age = _i(row, "Age")
            height_m = _f(row, "Height (m)")
            weight = _f(row, "Weight (kg)")
            fat = _f(row, "Fat_Percentage")
            if age is None or height_m is None or weight is None or fat is None:
                continue
            level = _S3_LEVEL_MAP.get(str(_i(row, "Experience_Level") or ""))
            anchors.append(
                Anchor(
                    raw_user_id=f"s3:{idx}",
                    source="s3",
                    sex=sex,  # type: ignore[arg-type]
                    age_years=age,
                    height_cm=height_m * 100.0,
                    weight_kg=weight,
                    body_fat_percent=fat,
                    training_frequency_per_week=_i(row, "Workout_Frequency (days/week)"),
                    avg_session_min=(
                        session_hours * 60.0
                        if (session_hours := _f(row, "Session_Duration (hours)"))
                        is not None
                        else None
                    ),
                    training_level=level,  # type: ignore[arg-type]
                    # goal не задан в S3 → выводим в synthesize._infer_goal.
                    goal=None,
                )
            )
    return anchors


# ---------- S4: body-fat-prediction-dataset ---------------------------------
# Kaggle URL: https://www.kaggle.com/datasets/fedesoriano/body-fat-prediction-dataset
# Колонки: Density, BodyFat, Age, Weight, Height, Neck, Chest, Abdomen,
# Hip, Thigh, Knee, Ankle, Biceps, Forearm, Wrist
# Здесь только мужчины (по описанию датасета); вес в фунтах, рост в дюймах.

_LB_TO_KG = 0.45359237
_INCH_TO_CM = 2.54


def parse_s4_csv(path: Path) -> list[Anchor]:
    """Body-fat prediction dataset → Anchor (sex='male' для всех записей)."""
    anchors: list[Anchor] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            age = _i(row, "Age")
            weight_lb = _f(row, "Weight")
            height_in = _f(row, "Height")
            fat = _f(row, "BodyFat")
            if age is None or weight_lb is None or height_in is None or fat is None:
                continue
            anchors.append(
                Anchor(
                    raw_user_id=f"s4:{idx}",
                    source="s4",
                    sex="male",
                    age_years=age,
                    height_cm=height_in * _INCH_TO_CM,
                    weight_kg=weight_lb * _LB_TO_KG,
                    body_fat_percent=fat,
                    # S4 не содержит поведенческих фичей — оставляем None.
                    training_frequency_per_week=None,
                    avg_session_min=None,
                    training_level=None,
                    goal=None,
                )
            )
    return anchors
