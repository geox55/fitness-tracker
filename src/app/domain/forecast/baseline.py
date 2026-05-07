"""Линейная регрессия по тренду InBody — baseline и fallback (REQ-12).

Никаких внешних зависимостей: чистый Python, чтобы тесты бежали без NumPy
и без БД. Этого достаточно для демонстрации в дипломе и сравнения с ML.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

# z-score для 80%-CI: 1.282 ≈ Φ⁻¹(0.9). Спрятано в константу — будем переиспользовать.
Z80 = 1.2815515655446004


@dataclass(frozen=True)
class LinearFit:
    slope: float
    intercept: float
    sigma: float  # стандартное отклонение остатков (residual standard error)
    span: float  # diapazon X (нужен для масштабирования CI на горизонт)
    n: int


def linear_fit(xs: Sequence[float], ys: Sequence[float]) -> LinearFit:
    """OLS для y = slope·x + intercept.

    Корректно работает на n≥2; при n<2 возвращает константный fit (slope=0).
    sigma — несмещённая оценка σ остатков для n≥3, иначе 0 (нет статистики).
    """
    n = len(xs)
    if n != len(ys):
        raise ValueError("xs and ys must have equal length")
    if n == 0:
        raise ValueError("at least one point is required")

    if n == 1:
        return LinearFit(slope=0.0, intercept=ys[0], sigma=0.0, span=0.0, n=1)

    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    if var_x == 0:
        return LinearFit(
            slope=0.0,
            intercept=mean_y,
            sigma=0.0,
            span=max(xs) - min(xs),
            n=n,
        )
    slope = cov / var_x
    intercept = mean_y - slope * mean_x

    if n >= 3:
        residuals = [
            y - (slope * x + intercept) for x, y in zip(xs, ys, strict=True)
        ]
        sse = sum(r * r for r in residuals)
        sigma = math.sqrt(sse / (n - 2))
    else:
        sigma = 0.0

    return LinearFit(
        slope=slope,
        intercept=intercept,
        sigma=sigma,
        span=max(xs) - min(xs),
        n=n,
    )


def linear_forecast(
    fit: LinearFit, x_target: float, *, ci_z: float = Z80
) -> tuple[float, float, float]:
    """Точка прогноза + CI на горизонте x_target.

    Прогнозная неопределённость растёт с расстоянием от центра наблюдений —
    учитываем простой формулой ширины CI: σ · √(1 + d_norm), где d_norm —
    нормированная дистанция от хвоста наблюдений до целевой точки.
    """
    point = fit.slope * x_target + fit.intercept
    if fit.sigma == 0:
        return point, point, point

    # x_target обычно > max(xs); считаем «как далеко мы за хвостом»
    distance_norm = (
        max(0.0, (x_target - fit.span) / fit.span) if fit.span > 0 else 0.0
    )
    half_width = ci_z * fit.sigma * math.sqrt(1.0 + distance_norm)
    return point, point - half_width, point + half_width


def physiological_clip_kg(
    base_value: float,
    point: float,
    *,
    horizon_weeks: int,
    max_per_week: float = 1.5,
) -> float:
    """Не позволяем модели экстраполировать резкие тренды (Edge case §10).

    `base_value` — последнее наблюдение, `point` — прогноз;
    разница ограничена ±max_per_week·horizon. Применяется только к весу;
    для жира/мышц аналогичные клипы — см. predictor.py.
    """
    delta = point - base_value
    cap = max_per_week * horizon_weeks
    if delta > cap:
        return base_value + cap
    if delta < -cap:
        return base_value - cap
    return point
