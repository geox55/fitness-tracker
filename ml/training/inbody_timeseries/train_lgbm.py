"""LightGBM quantile-регрессор для InBody-предиктора — основная модель диплома.

Зачем quantile, а не обычный regression:
- В spec 008 REQ-01 требуется **80%-доверительный интервал** на каждом
  горизонте. Bootstrap'ом считать дорого и шумно на малых выборках;
  LightGBM умеет нативно — обучается с `objective="quantile", alpha=q`
  для нужного квантиля.
- Три модели на каждый target: q=0.10 (нижняя граница), q=0.50 (точка),
  q=0.90 (верхняя). 80%-CI = [q10, q90].

Что обучаем:
- 3 target × 3 quantile = 9 LGBM-моделей, сохраняем в отдельных файлах.
- Гиперпараметры — фиксированные «sensible defaults» (умеренные
  `num_leaves`, ранний стоп по `val`-метрике). Тюнинг делается отдельно
  через `python -m ml.training.inbody_timeseries.tune` (out of scope
  первого прохода, но manifest позволяет легко обновить версию).
- early_stopping по val-сплиту → защита от переобучения при малом
  датасете.

Артефакты: `ml/models/inbody_pred/lgbm/v{semver}/{target}_q{int}.joblib`.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd

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

MODEL_NAME = "lgbm"
DEFAULT_VERSION = "0.1.0"
QUANTILES: tuple[float, ...] = (0.10, 0.50, 0.90)

# Значения подобраны для маленького датасета (тысячи строк) — иначе
# LGBM легко переобучится. num_leaves=15 ≈ глубина 4, learning_rate
# мал, чтобы early_stopping_rounds успел сработать.
DEFAULT_PARAMS: dict[str, float | int | str] = {
    "objective": "quantile",
    "metric": "quantile",
    "learning_rate": 0.05,
    "num_leaves": 15,
    "min_data_in_leaf": 20,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.9,
    "bagging_freq": 5,
    "verbosity": -1,
    "random_state": 42,
}
NUM_BOOST_ROUND = 500
EARLY_STOPPING = 30


@dataclass(frozen=True)
class FittedQuantiles:
    """3 модели одного target — низкий, средний, высокий квантиль."""

    target: str
    boosters: dict[float, lgb.Booster]


def _drop_nan_target(
    X: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.Series]:
    mask = y.notna()
    return X.loc[mask], y.loc[mask]


def _train_quantile(
    *,
    quantile: float,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
) -> lgb.Booster:
    params = {**DEFAULT_PARAMS, "alpha": quantile}
    train_set = lgb.Dataset(X_train, label=y_train)
    val_set = lgb.Dataset(X_val, label=y_val, reference=train_set)
    booster = lgb.train(
        params,
        train_set,
        num_boost_round=NUM_BOOST_ROUND,
        valid_sets=[val_set],
        valid_names=["val"],
        callbacks=[
            lgb.early_stopping(EARLY_STOPPING, verbose=False),
            lgb.log_evaluation(0),  # silent
        ],
    )
    return booster


def _fit_one_target(
    *,
    target: str,
    train: DatasetSplit,
    val: DatasetSplit,
) -> FittedQuantiles:
    X_train = train.X[list(FEATURE_COLUMNS)]
    y_train = train.y[target]
    X_train, y_train = _drop_nan_target(X_train, y_train)

    X_val = val.X[list(FEATURE_COLUMNS)]
    y_val = val.y[target]
    X_val, y_val = _drop_nan_target(X_val, y_val)

    boosters: dict[float, lgb.Booster] = {}
    for q in QUANTILES:
        boosters[q] = _train_quantile(
            quantile=q,
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
        )
    return FittedQuantiles(target=target, boosters=boosters)


def _evaluate_target(
    *,
    target: str,
    fitted: FittedQuantiles,
    test: DatasetSplit,
) -> dict[str, float]:
    X_test = test.X[list(FEATURE_COLUMNS)]
    y_test = test.y[target]

    pred_q10 = np.asarray(fitted.boosters[0.10].predict(X_test))
    pred_q50 = np.asarray(fitted.boosters[0.50].predict(X_test))
    pred_q90 = np.asarray(fitted.boosters[0.90].predict(X_test))

    metrics = compute_metrics(
        y_true=y_test, y_pred=pred_q50, q_low=pred_q10, q_high=pred_q90
    )
    return metrics.to_dict()


def _q_suffix(q: float) -> str:
    """0.10 → 'q10', 0.50 → 'q50', 0.90 → 'q90' — короткое стабильное имя."""
    return f"q{round(q * 100)}"


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

    metrics_block: dict[str, dict[str, float]] = {}

    for target in PREDICT_TARGETS:
        fitted = _fit_one_target(
            target=target, train=splits["train"], val=splits["val"]
        )
        for q, booster in fitted.boosters.items():
            joblib.dump(booster, out_dir / f"{target}_{_q_suffix(q)}.joblib")
        metrics_block[target] = _evaluate_target(
            target=target, fitted=fitted, test=splits["test"]
        )

    manifest = ModelManifest(
        model_name=MODEL_NAME,
        model_version=f"inbody-pred-{MODEL_NAME}-{version}",
        feature_columns=list(FEATURE_COLUMNS),
        targets=list(PREDICT_TARGETS),
        has_quantiles=True,
        quantiles=QUANTILES,
        dataset_sha256=sha256_file(dataset_csv),
        dataset_rows=len(df),
        trained_at=now_iso(),
        metrics=metrics_block,
        hyperparams={
            "num_boost_round": NUM_BOOST_ROUND,
            "early_stopping_rounds": EARLY_STOPPING,
            **{k: v for k, v in DEFAULT_PARAMS.items() if k != "alpha"},
        },
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Train LightGBM quantile-predictor (spec 008 main model)"
    )
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
    print(f"Saved {manifest.model_version} to {args.out_root}/{MODEL_NAME}/v{args.version}")
    for target, m in manifest.metrics.items():
        cov = m.get("ci80_coverage", 0.0)
        print(
            f"  {target}: MAE={m['mae']:.4f} "
            f"RMSE={m['rmse']:.4f} R²={m['r2']:.3f} CI80={cov:.2f}"
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
