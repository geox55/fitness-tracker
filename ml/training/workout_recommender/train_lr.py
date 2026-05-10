"""Logistic Regression baseline для рекомендатора.

Линейная модель — простой ориентир: показывает, какую часть сигнала
можно поймать без нелинейностей. На spec 006 фичи довольно линейные
(goal_*, level_*, group_*), поэтому LR должен взять основу; LGBM
проявит себя на subtle сочетаниях (например, advanced × beginner).

Артефакт: ml/models/workout_rec/lr/v{semver}/lr.joblib (Pipeline:
StandardScaler + LogisticRegression).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data import load_dataset_c, split_dataset
from .evaluate import DEFAULT_K, compute_metrics
from .manifest import ModelManifest, model_dir, now_iso, sha256_file, write_manifest

MODEL_NAME = "lr"
DEFAULT_VERSION = "0.1.0"


def train(
    *, dataset_csv: Path, out_root: Path, version: str = DEFAULT_VERSION
) -> ModelManifest:
    df = load_dataset_c(dataset_csv)
    splits = split_dataset(df)
    train_split = splits["train"]
    test_split = splits["test"]

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "lr",
                LogisticRegression(
                    # class_weight=balanced — вес классов обратно
                    # пропорциональный, лечит imbalance без ресэмплинга.
                    class_weight="balanced",
                    max_iter=200,
                    random_state=42,
                ),
            ),
        ]
    )
    pipeline.fit(train_split.X, train_split.y)
    y_score = pipeline.predict_proba(test_split.X)[:, 1]

    metrics = compute_metrics(
        y_true=test_split.y,
        y_score=y_score,
        groups=test_split.group,
        k=DEFAULT_K,
    )

    out_dir = model_dir(root=out_root, model_name=MODEL_NAME, version=version)
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, out_dir / f"{MODEL_NAME}.joblib")

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
            "class_weight": "balanced",
            "max_iter": 200,
            "random_state": 42,
        },
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LogisticRegression baseline")
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
