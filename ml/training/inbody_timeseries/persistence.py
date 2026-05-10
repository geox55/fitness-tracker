"""Persistence sanity-baseline: предсказываем Δ=0 ⇒ «всё останется как есть».

Никакая модель не должна работать **хуже**, чем эта. Если LGBM/Ridge не
бьют persistence — что-то не так с фичами или данными. Метрики этого
baseline идут в сравнительную таблицу для главы магистерской работы.

Хранить артефакт не нужно — predict_persistence — это `np.zeros(n)`.
Но manifest всё равно сохраняем, чтобы compare.py читал все три модели
по единой схеме.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from .data import (
    FEATURE_COLUMNS,
    PREDICT_TARGETS,
    DatasetSplit,
    load_dataset_b,
    split_dataset,
)
from .evaluate import compute_metrics
from .manifest import (
    ModelManifest,
    model_dir,
    now_iso,
    sha256_file,
    write_manifest,
)

MODEL_NAME = "persistence"
DEFAULT_VERSION = "0.1.0"


def _evaluate_one(target: str, test: DatasetSplit) -> dict[str, float]:
    n = len(test.y)
    y_pred = np.zeros(n, dtype=float)
    return compute_metrics(y_true=test.y[target], y_pred=y_pred).to_dict()


def train(
    *,
    dataset_csv: Path,
    out_root: Path,
    version: str = DEFAULT_VERSION,
) -> ModelManifest:
    df = load_dataset_b(dataset_csv)
    splits = split_dataset(df)
    out_dir = model_dir(root=out_root, model_name=MODEL_NAME, version=version)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics_block = {target: _evaluate_one(target, splits["test"]) for target in PREDICT_TARGETS}
    manifest = ModelManifest(
        model_name=MODEL_NAME,
        model_version=f"inbody-pred-{MODEL_NAME}-{version}",
        feature_columns=list(FEATURE_COLUMNS),
        targets=list(PREDICT_TARGETS),
        has_quantiles=False,
        quantiles=(0.5,),
        dataset_sha256=sha256_file(dataset_csv),
        dataset_rows=len(df),
        trained_at=now_iso(),
        metrics=metrics_block,
        hyperparams={},
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Persistence baseline (Δ=0)")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument(
        "--out-root", type=Path, default=Path("ml/models/inbody_pred")
    )
    parser.add_argument("--version", type=str, default=DEFAULT_VERSION)
    args = parser.parse_args(argv)
    manifest = train(
        dataset_csv=args.dataset,
        out_root=args.out_root,
        version=args.version,
    )
    print(f"Saved {manifest.model_version}")
    for target, m in manifest.metrics.items():
        print(f"  {target}: MAE={m['mae']:.4f} RMSE={m['rmse']:.4f} R²={m['r2']:.3f}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
