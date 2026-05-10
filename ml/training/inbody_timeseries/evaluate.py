"""Метрики оценки моделей на test-сплите.

Считаем (на каждый target):
- MAE — средняя абсолютная ошибка point-estimate'а;
- RMSE — корень из MSE; чувствителен к выбросам;
- R² — доля объяснённой дисперсии;
- ci80_coverage — для quantile-моделей: % точек, попавших в [q10, q90];
                  должно быть ≈0.80 для калиброванной модели.

Метрики кладутся в manifest.json и используются в `compare.py` для
сводной таблицы (для главы магистерской работы).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


@dataclass(frozen=True)
class TargetMetrics:
    mae: float
    rmse: float
    r2: float
    ci80_coverage: float | None  # None для моделей без quantile

    def to_dict(self) -> dict[str, float]:
        d: dict[str, float] = {
            "mae": float(self.mae),
            "rmse": float(self.rmse),
            "r2": float(self.r2),
        }
        if self.ci80_coverage is not None:
            d["ci80_coverage"] = float(self.ci80_coverage)
        return d


def compute_metrics(
    *,
    y_true: pd.Series,
    y_pred: np.ndarray,
    q_low: np.ndarray | None = None,
    q_high: np.ndarray | None = None,
) -> TargetMetrics:
    """Метрики для одного target'а.

    `y_true` может содержать NaN (например, у анкеров без muscle_mass_kg);
    отбрасываем такие строки до подсчёта — sklearn не любит NaN.
    `q_low/q_high` нужны только для CI coverage; если они переданы,
    маска NaN применяется и к ним для согласованности.
    """
    mask = y_true.notna().to_numpy()
    yt = y_true.to_numpy()[mask]
    yp = y_pred[mask]

    mae = mean_absolute_error(yt, yp)
    # sklearn 1.4+ переименовал squared в `mean_squared_error(squared=False)` →
    # `root_mean_squared_error`; используем явный sqrt чтобы не зависеть от версии.
    rmse = float(np.sqrt(mean_squared_error(yt, yp)))
    r2 = float(r2_score(yt, yp)) if len(np.unique(yt)) > 1 else 0.0

    coverage: float | None = None
    if q_low is not None and q_high is not None:
        ql = q_low[mask]
        qh = q_high[mask]
        inside = (yt >= ql) & (yt <= qh)
        coverage = float(inside.mean()) if inside.size else 0.0

    return TargetMetrics(mae=float(mae), rmse=rmse, r2=r2, ci80_coverage=coverage)
