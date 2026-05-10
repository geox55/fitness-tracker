"""Training pipeline для AI-предиктора InBody — spec 008 + 012 (главный
ML-блок диплома Маши).

Поддерживаемые модели:
- `persistence` — sanity baseline: Δ=0 (предсказываем «всё останется как есть»);
- `ridge`      — линейная регрессия с L2-регуляризацией (sklearn);
- `lgbm`       — LightGBM с **quantile**-loss (q=0.1, 0.5, 0.9), даёт
                  80%-CI прямо из коробки, без bootstrap'а — что точно
                  соответствует REQ-01 spec 008 («80% доверительный интервал»).

Все модели обучаются на one-step-задаче (next-week дельта), рекурсивно
применяются для горизонтов 1/2/4 — это совпадает с контрактом
`domain.forecast.predictor.build_forecast`. Артефакт сохраняется в
`ml/models/inbody_pred/{model}/v{semver}/` с manifest.json, чтобы рантайм
мог подцепить его без изменений в коде сервиса.
"""

from .data import (
    FEATURE_COLUMNS,
    PREDICT_TARGETS,
    DatasetSplit,
    load_dataset_b,
    make_features_targets,
)

__all__ = [
    "FEATURE_COLUMNS",
    "PREDICT_TARGETS",
    "DatasetSplit",
    "load_dataset_b",
    "make_features_targets",
]
