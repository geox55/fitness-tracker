"""Training pipeline для AI-генератора тренировок (spec 006, диплом Егора).

Задача: бинарная классификация «релевантно ли это упражнение пользователю».
Обучаемся на Dataset-C (rule-based labels из ml.etl.workout_recommender).

Что внутри:
- `data.py` — чтение CSV + feature engineering (one-hot для goal/level/group/region);
- `train_lgbm.py` — LightGBM Classifier (binary objective + class_weight balanced);
- `train_lr.py` — LogisticRegression baseline (sklearn);
- `popularity.py` — global rate baseline (predict mean(label) для всех);
- `evaluate.py` — ROC-AUC, PR-AUC, precision@K, recall@K;
- `compare.py` — сводная таблица для главы магистерской.
"""

from .data import (
    EXERCISE_FEATURES,
    USER_FEATURES,
    DatasetSplit,
    load_dataset_c,
    make_features_targets,
)

__all__ = [
    "EXERCISE_FEATURES",
    "USER_FEATURES",
    "DatasetSplit",
    "load_dataset_c",
    "make_features_targets",
]
