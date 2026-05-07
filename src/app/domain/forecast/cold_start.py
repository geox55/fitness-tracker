"""Cold-start прогноз для пользователей с <4 InBody (REQ-07).

Используем cross-user baseline на основе цели + типичной траектории. Это
не «модель» в смысле обучения — это эвристика; после накопления данных
она будет заменена на ML cross-user transfer (см. spec 008 §2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Goal = Literal["weight_loss", "muscle_gain", "maintenance"]

# Типичные недельные дельты по цели (среднее по литературе и фитнес-практике).
# Источники зафиксированы в магистерской работе — здесь только числа.
_GOAL_TRAJECTORIES: dict[Goal | None, tuple[float, float, float]] = {
    # (Δweight_kg/week, Δfat%/week, Δmuscle_kg/week)
    "weight_loss": (-0.5, -0.25, +0.05),
    "muscle_gain": (+0.25, -0.10, +0.20),
    "maintenance": (0.0, 0.0, 0.0),
    None: (0.0, 0.0, 0.0),
}

# CI для cold-start заведомо широкий — мы ничего не знаем о пользователе.
_COLD_START_CI = {
    "weight_kg": 1.5,    # ±1.5 кг на горизонте 4 недели
    "body_fat_percent": 2.0,
    "muscle_mass_kg": 1.0,
}


@dataclass(frozen=True)
class ColdStartPoint:
    horizon_weeks: int
    point: float
    ci_low: float
    ci_high: float


def cold_start_forecast(
    *,
    base_weight_kg: float,
    base_body_fat_percent: float,
    base_muscle_mass_kg: float | None,
    goal: Goal | None,
    horizons: list[int],
) -> dict[str, list[ColdStartPoint]]:
    """Линейная экстраполяция базовой точки по типичной траектории."""
    delta_w, delta_fat, delta_muscle = _GOAL_TRAJECTORIES[goal]
    out: dict[str, list[ColdStartPoint]] = {
        "weight_kg": [],
        "body_fat_percent": [],
        "muscle_mass_kg": [],
    }

    for h in horizons:
        # Вес
        wp = base_weight_kg + delta_w * h
        wci = _COLD_START_CI["weight_kg"] * (h / 4)
        out["weight_kg"].append(
            ColdStartPoint(
                horizon_weeks=h, point=wp, ci_low=wp - wci, ci_high=wp + wci
            )
        )
        # Жир %
        fp = base_body_fat_percent + delta_fat * h
        fci = _COLD_START_CI["body_fat_percent"] * (h / 4)
        out["body_fat_percent"].append(
            ColdStartPoint(
                horizon_weeks=h, point=fp, ci_low=fp - fci, ci_high=fp + fci
            )
        )
        # Мышечная масса (если базовое значение неизвестно — оставляем 0,
        # сервис покажет null в API; точку мы всё равно нужно вернуть для
        # симметрии — но клиппинг ограничит «выдумывание»).
        if base_muscle_mass_kg is None:
            out["muscle_mass_kg"].append(
                ColdStartPoint(
                    horizon_weeks=h, point=0.0, ci_low=0.0, ci_high=0.0
                )
            )
        else:
            mp = base_muscle_mass_kg + delta_muscle * h
            mci = _COLD_START_CI["muscle_mass_kg"] * (h / 4)
            out["muscle_mass_kg"].append(
                ColdStartPoint(
                    horizon_weeks=h, point=mp, ci_low=mp - mci, ci_high=mp + mci
                )
            )

    return out
