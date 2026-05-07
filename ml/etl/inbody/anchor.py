"""Общий формат `Anchor` — стартовая точка для синтеза траектории.

Парсеры S3/S4 приводят свои строки к этому виду; дальше pipeline работает
только с Anchor, не зная, откуда строка пришла. Это позволяет легко
добавлять новые источники в будущем (S5, например, MyFitnessPal-открытые).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Sex = Literal["male", "female"]
Goal = Literal["weight_loss", "muscle_gain", "maintenance"]
TrainingLevel = Literal["beginner", "intermediate", "advanced"]


@dataclass(frozen=True)
class Anchor:
    """Поперечный срез: фичи на момент t=0 для синтеза временного ряда.

    Чем больше полей известно, тем правдоподобнее траектория. Минимум
    обязательных: sex, age, height_cm, weight_kg, body_fat_percent —
    без них синтезировать смысла нет.
    """

    raw_user_id: str  # сырой айдишник из источника, до анонимизации
    source: str  # 's3' | 's4'

    sex: Sex
    age_years: int
    height_cm: float
    weight_kg: float
    body_fat_percent: float

    muscle_mass_kg: float | None = None
    bmr_kcal: float | None = None  # вычисляется в impute.py если None

    # Поведенческие фичи (только из S3 — S4 их не содержит).
    training_frequency_per_week: int | None = None
    avg_session_min: float | None = None
    goal: Goal | None = None
    training_level: TrainingLevel | None = None
