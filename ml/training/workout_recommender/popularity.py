"""Sanity baseline: popularity = global mean(label).

Каждому (user, exercise) присваиваем один и тот же score (среднюю долю
positives на train). На бинарной классификации даёт ROC-AUC=0.5
(случайное упорядочивание) — нижний порог, ниже которого ни Logistic,
ни LGBM падать не должны.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from .data import load_dataset_c, split_dataset
from .evaluate import DEFAULT_K, compute_metrics
from .manifest import ModelManifest, model_dir, now_iso, sha256_file, write_manifest

MODEL_NAME = "popularity"
DEFAULT_VERSION = "0.1.0"


def train(
    *, dataset_csv: Path, out_root: Path, version: str = DEFAULT_VERSION
) -> ModelManifest:
    df = load_dataset_c(dataset_csv)
    splits = split_dataset(df)

    train_split = splits["train"]
    test_split = splits["test"]
    global_rate = float(train_split.y.mean())

    n_test = len(test_split.y)
    y_score = np.full(n_test, global_rate, dtype=float)

    metrics = compute_metrics(
        y_true=test_split.y,
        y_score=y_score,
        groups=test_split.group,
        k=DEFAULT_K,
    )

    out_dir = model_dir(root=out_root, model_name=MODEL_NAME, version=version)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = ModelManifest(
        model_name=MODEL_NAME,
        model_version=f"workout-rec-{MODEL_NAME}-{version}",
        feature_columns=[],
        dataset_sha256=sha256_file(dataset_csv),
        dataset_rows=len(df),
        dataset_positive_ratio=float(df["label"].mean()),
        trained_at=now_iso(),
        metrics=metrics.to_dict(),
        hyperparams={"global_rate_train": global_rate},
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Popularity baseline")
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
