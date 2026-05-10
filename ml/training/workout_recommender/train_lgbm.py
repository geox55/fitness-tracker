"""LightGBM Classifier — основная модель recommender'а из диплома Егора.

Объект — binary log-loss; predict_proba даёт скор «релевантно?».
class_weight='balanced' автоматически выставляет sample_weight по
обратной частоте: на 67% positives это лёгкий тильт в сторону negatives,
на сильном imbalance отрабатывает корректно.

Гиперпараметры — sensible defaults для табличной задачи среднего размера
(~80k строк, ~30 колонок):
- num_leaves=31 — стандартное значение, глубина ~5;
- min_data_in_leaf=50 — защита от листьев из 1 пользователя;
- early_stopping по val log-loss → защита от переобучения.

Артефакт: ml/models/workout_rec/lgbm/v{semver}/lgbm.joblib (lgb.Booster).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np

from .data import load_dataset_c, split_dataset
from .evaluate import DEFAULT_K, compute_metrics
from .manifest import ModelManifest, model_dir, now_iso, sha256_file, write_manifest

MODEL_NAME = "lgbm"
DEFAULT_VERSION = "0.1.0"

DEFAULT_PARAMS: dict[str, float | int | str] = {
    "objective": "binary",
    "metric": "binary_logloss",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_data_in_leaf": 50,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.9,
    "bagging_freq": 5,
    "verbosity": -1,
    "is_unbalance": True,  # эквивалент class_weight=balanced для бинарной
    "random_state": 42,
}
NUM_BOOST_ROUND = 600
EARLY_STOPPING = 30


def train(
    *, dataset_csv: Path, out_root: Path, version: str = DEFAULT_VERSION
) -> ModelManifest:
    df = load_dataset_c(dataset_csv)
    splits = split_dataset(df)
    train_split = splits["train"]
    val_split = splits["val"]
    test_split = splits["test"]

    train_set = lgb.Dataset(train_split.X, label=train_split.y)
    val_set = lgb.Dataset(val_split.X, label=val_split.y, reference=train_set)

    booster = lgb.train(
        DEFAULT_PARAMS,
        train_set,
        num_boost_round=NUM_BOOST_ROUND,
        valid_sets=[val_set],
        valid_names=["val"],
        callbacks=[
            lgb.early_stopping(EARLY_STOPPING, verbose=False),
            lgb.log_evaluation(0),
        ],
    )
    y_score = np.asarray(booster.predict(test_split.X))

    metrics = compute_metrics(
        y_true=test_split.y,
        y_score=y_score,
        groups=test_split.group,
        k=DEFAULT_K,
    )

    out_dir = model_dir(root=out_root, model_name=MODEL_NAME, version=version)
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(booster, out_dir / f"{MODEL_NAME}.joblib")

    manifest = ModelManifest(
        model_name=MODEL_NAME,
        model_version=f"workout-rec-{MODEL_NAME}-{version}",
        feature_columns=list(train_split.X.columns),
        dataset_sha256=sha256_file(dataset_csv),
        dataset_rows=len(df),
        dataset_positive_ratio=float(df["label"].mean()),
        trained_at=now_iso(),
        metrics=metrics.to_dict(),
        hyperparams={
            "num_boost_round": NUM_BOOST_ROUND,
            "early_stopping_rounds": EARLY_STOPPING,
            "best_iteration": int(booster.best_iteration or 0),
            **{k: v for k, v in DEFAULT_PARAMS.items()},
        },
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LightGBM recommender")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument(
        "--out-root", type=Path, default=Path("ml/models/workout_rec")
    )
    parser.add_argument("--version", type=str, default=DEFAULT_VERSION)
    args = parser.parse_args(argv)
    m = train(
        dataset_csv=args.dataset, out_root=args.out_root, version=args.version
    )
    print(f"Saved {m.model_version}")
    print(
        f"  ROC-AUC={m.metrics['roc_auc']:.3f} PR-AUC={m.metrics['pr_auc']:.3f}"
        f"  P@K={m.metrics['precision_at_k']:.3f}"
        f"  R@K={m.metrics['recall_at_k']:.3f}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
