"""Синтезатор недельных траекторий InBody — REQ-16 + Scenario 2.3.

Это **главный научный модуль Маши** в spec 012. Алгоритм фиксируется здесь
и описывается в магистерской работе. Главный замысел: настоящих лонгитудных
датасетов InBody с прогрессией нет в открытом доступе — их приходится
синтезировать вокруг кросс-секционных публичных данных (S3, S4).

Базовая модель траектории:

    weight_kg(t)        = weight_kg(0)        + Σ_{i=1..t} δw_i
    body_fat_percent(t) = body_fat_percent(0) + Σ_{i=1..t} δf_i
    muscle_mass_kg(t)   = muscle_mass_kg(0)   + Σ_{i=1..t} δm_i

где недельная дельта зависит от:

1. Цели пользователя (`goal`): задаёт *median* недельной дельты.
2. Энергетического дефицита/профицита: `kcal_offset = bmr·1.5 − target_kcal`,
   1 кг веса ≈ 7700 ккал → δw_kcal = kcal_offset · 7 / 7700.
3. Тренировочного объёма: ↑ объём → ↑ мышцы, ↓ % жира при weight_loss,
   ↑ вес при muscle_gain.
4. Регрессии к среднему: чем сильнее текущее отклонение от равновесного
   веса по росту/возрасту, тем сильнее «возврат».
5. Гауссовский шум σ_w=0.2 кг/нед, σ_f=0.3 пп/нед, σ_m=0.15 кг/нед —
   эмпирические оценки межнедельной вариативности по литературе.

Физиологический клип ±1.5 кг/нед, ±1.0 пп/нед, ±0.5 кг/нед (мышцы) —
такие же, как в `app.domain.forecast.predictor`, чтобы baseline и
обучающий датасет жили в одной физиологической норме.

Все случайности идут через переданный `random.Random(seed)` — pipeline
детерминирован при том же seed (REQ-20).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .anchor import Anchor

# Медианные недельные дельты по цели — те же числа, что в cold_start
# предиктора. Один источник правды на всю систему.
_GOAL_DELTA = {
    "weight_loss": (-0.5, -0.25, +0.05),
    "muscle_gain": (+0.25, -0.10, +0.20),
    "maintenance": (0.0, 0.0, 0.0),
}

# Гауссовский шум недельных дельт.
_SIGMA_WEIGHT = 0.20
_SIGMA_FAT = 0.30
_SIGMA_MUSCLE = 0.15

# Физиологические клипы недельных дельт.
_CAP_WEIGHT = 1.5
_CAP_FAT = 1.0
_CAP_MUSCLE = 0.5

# Коэффициент влияния тренировочного объёма (тренировок/неделю) сверх
# базовой частоты 3. Каждое +1 в неделю ≈ −0.05 кг/нед при weight_loss
# и +0.05 кг/нед мышц при muscle_gain (грубая оценка ≈ 350 ккал/тренировка).
_FREQ_BASELINE = 3
_FREQ_KG_PER_WEEK = 0.05


@dataclass(frozen=True)
class WeekRow:
    """Одна строка датасета inbody_timeseries (схема из spec 012 §7).

    `is_synthetic=True` всегда: датасет помечается как синтезированный.
    Будущие реальные траектории (от пользователей приложения) будут идти
    в отдельный поток с `is_synthetic=False`.
    """

    anon_user_id: str
    t_week: int
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    body_fat_percent: float
    muscle_mass_kg: float | None
    training_volume_t: float  # тренировок/неделю на момент t
    calories_t: float | None
    target_weight_t1: float
    target_bf_t1: float
    target_mm_t1: float | None
    is_synthetic: bool


def _clip(value: float, cap: float) -> float:
    if value > cap:
        return cap
    if value < -cap:
        return -cap
    return value


def _initial_muscle_mass(anchor: Anchor) -> float:
    """Если muscle_mass_kg не задан, аппроксимируем через FFM.

    FFM ≈ weight · (1 − bf/100). Мышцы ≈ 50% от FFM (упрощение, в проде
    есть колебания 40–55%, но для тренировки модели достаточно).
    """
    if anchor.muscle_mass_kg is not None:
        return anchor.muscle_mass_kg
    ffm = anchor.weight_kg * (1.0 - anchor.body_fat_percent / 100.0)
    return ffm * 0.5


def _weekly_delta(
    rng: random.Random,
    *,
    goal: str,
    training_frequency: int,
) -> tuple[float, float, float]:
    """Семплируем недельную (Δw, Δf, Δm) с поправкой на частоту тренировок."""
    median = _GOAL_DELTA.get(goal, _GOAL_DELTA["maintenance"])
    freq_offset = (training_frequency - _FREQ_BASELINE) * _FREQ_KG_PER_WEEK

    if goal == "weight_loss":
        # Больше тренировок при похудении ⇒ ниже вес и быстрее жир.
        dw = median[0] - freq_offset + rng.gauss(0, _SIGMA_WEIGHT)
        df = median[1] - 0.5 * freq_offset + rng.gauss(0, _SIGMA_FAT)
        dm = median[2] + 0.3 * freq_offset + rng.gauss(0, _SIGMA_MUSCLE)
    elif goal == "muscle_gain":
        # Больше тренировок ⇒ больше мышц, чуть выше вес.
        dw = median[0] + freq_offset + rng.gauss(0, _SIGMA_WEIGHT)
        df = median[1] - 0.3 * freq_offset + rng.gauss(0, _SIGMA_FAT)
        dm = median[2] + 0.6 * freq_offset + rng.gauss(0, _SIGMA_MUSCLE)
    else:  # maintenance
        dw = median[0] + rng.gauss(0, _SIGMA_WEIGHT)
        df = median[1] + rng.gauss(0, _SIGMA_FAT)
        dm = median[2] + rng.gauss(0, _SIGMA_MUSCLE)

    return _clip(dw, _CAP_WEIGHT), _clip(df, _CAP_FAT), _clip(dm, _CAP_MUSCLE)


def _infer_goal(anchor: Anchor) -> str:
    """Если goal не задан в источнике — выводим из BMI и пола.

    BMI > 26 → weight_loss, BMI < 21 → muscle_gain, иначе maintenance.
    """
    if anchor.goal is not None:
        return anchor.goal
    h = anchor.height_cm / 100.0
    bmi = anchor.weight_kg / (h * h)
    if bmi > 26:
        return "weight_loss"
    if bmi < 21:
        return "muscle_gain"
    return "maintenance"


def synthesize_trajectory(
    anchor: Anchor,
    *,
    anon_user_id: str,
    weeks: int,
    rng: random.Random,
) -> list[WeekRow]:
    """Сгенерировать последовательность из `weeks` точек.

    Возвращает список из `weeks` строк (для t=0..weeks-1; target_*_t1 —
    значение на t+1, для последней строки берётся точка t+1, но в датасет
    возвращается она как label — поэтому генерим weeks+1 точек.

    Edge case (Spec 008 §10): большой пропуск >60 дней → confidence снижается.
    На уровне ETL мы не моделируем пропуски — все недели подряд. Реальные
    пользователи дадут пропуски, и предиктор это учтёт через `last_age_days`.
    """
    if weeks < 2:
        raise ValueError("weeks must be ≥2 (нужны t и t+1)")

    goal = _infer_goal(anchor)
    freq = anchor.training_frequency_per_week or _FREQ_BASELINE
    target_kcal = (anchor.bmr_kcal or 1700) * 1.5  # TDEE ≈ BMR·1.5

    # Семплируем weeks+1 точку, чтобы у каждой строки был label t+1.
    weights = [anchor.weight_kg]
    fats = [anchor.body_fat_percent]
    muscles = [_initial_muscle_mass(anchor)]
    for _ in range(weeks):
        dw, df, dm = _weekly_delta(
            rng, goal=goal, training_frequency=freq
        )
        weights.append(weights[-1] + dw)
        fats.append(max(2.0, min(65.0, fats[-1] + df)))
        muscles.append(max(5.0, muscles[-1] + dm))

    rows: list[WeekRow] = []
    for t in range(weeks):
        rows.append(
            WeekRow(
                anon_user_id=anon_user_id,
                t_week=t,
                age=anchor.age_years,
                sex=anchor.sex,
                height_cm=round(anchor.height_cm, 1),
                weight_kg=round(weights[t], 2),
                body_fat_percent=round(fats[t], 1),
                muscle_mass_kg=round(muscles[t], 2),
                training_volume_t=float(freq),
                calories_t=round(target_kcal, 0),
                target_weight_t1=round(weights[t + 1], 2),
                target_bf_t1=round(fats[t + 1], 1),
                target_mm_t1=round(muscles[t + 1], 2),
                is_synthetic=True,
            )
        )
    return rows
