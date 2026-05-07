"""Заполнение пропущенных полей и фильтрация выбросов — REQ-14, Edge §10.

BMR считаем по Mifflin-St Jeor (повторяем формулу из app.domain.calc.bmr,
чтобы ETL не зависел от приложения — этот пайплайн должен запускаться
без доступа к коду app/, например, на отдельной ML-машине).
"""

from __future__ import annotations

from dataclasses import replace

from .anchor import Anchor


def bmr_mifflin_st_jeor(
    *, weight_kg: float, height_cm: float, age_years: int, sex: str
) -> float:
    """Та же формула, что в src/app/domain/calc/bmr.py.

    Дублирование осознанное: ETL должен запускаться независимо от Python-
    пакета приложения. Любое изменение формулы в одном месте требует
    зеркального изменения здесь — оба покрыты юнит-тестами.
    """
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age_years
    if sex == "male":
        return base + 5
    if sex == "female":
        return base - 161
    raise ValueError(f"unknown sex: {sex!r}")


def bmi(weight_kg: float, height_cm: float) -> float:
    h = height_cm / 100.0
    if h <= 0:
        raise ValueError("height_cm must be positive")
    return weight_kg / (h * h)


def is_outlier(anchor: Anchor) -> bool:
    """Edge case §10: BMI<10 или BMI>70 — отбрасываем.

    Также убираем явно невозможные значения body_fat (<2% или >65%) —
    в публичных датасетах встречаются мусорные строки.
    """
    try:
        b = bmi(anchor.weight_kg, anchor.height_cm)
    except ValueError:
        return True
    if not (10 <= b <= 70):
        return True
    if not (2 <= anchor.body_fat_percent <= 65):
        return True
    return anchor.age_years < 14 or anchor.age_years > 90


def impute_bmr(anchor: Anchor) -> Anchor:
    """REQ-14: если BMR нет — посчитать по Mifflin-St Jeor."""
    if anchor.bmr_kcal is not None:
        return anchor
    bmr = bmr_mifflin_st_jeor(
        weight_kg=anchor.weight_kg,
        height_cm=anchor.height_cm,
        age_years=anchor.age_years,
        sex=anchor.sex,
    )
    return replace(anchor, bmr_kcal=bmr)


def filter_and_impute(anchors: list[Anchor]) -> tuple[list[Anchor], dict[str, int]]:
    """Прогнать список через outlier-фильтр и BMR-imputation.

    Возвращаем кортеж (clean, stats) — для отчёта (REQ-09 говорит про
    report; для Dataset-B это полезно тем же способом).
    """
    clean: list[Anchor] = []
    stats = {"input": len(anchors), "outliers": 0, "imputed_bmr": 0, "kept": 0}
    for a in anchors:
        if is_outlier(a):
            stats["outliers"] += 1
            continue
        if a.bmr_kcal is None:
            a = impute_bmr(a)
            stats["imputed_bmr"] += 1
        clean.append(a)
    stats["kept"] = len(clean)
    return clean, stats
