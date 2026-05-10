"""Ridge baseline для InBody-предиктора.

Линейная регрессия с L2-регуляризацией. На малых выборках работает лучше,
чем чистая OLS, и устойчива к мультиколлинеарности (bmi/ffm/weight_kg
коррелированы — это нормально, Ridge это переживёт).

Что обучаем:
- Один Ridge на каждый target из PREDICT_TARGETS (3 модели).
- alpha подбирается через GridSearchCV с GroupKFold по anon_user_id —
  no-leakage между fold'ами одного пользователя.
- Перед обучением `muscle_mass_kg` импутируется медианой train (LightGBM
  такого не требует, но Ridge — да).

Сохраняем как `ml/models/inbody_pred/ridge/v{semver}/{target}.joblib`.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

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

MODEL_NAME = "ridge"
DEFAULT_VERSION = "0.1.0"
ALPHA_GRID = (0.1, 1.0, 3.0, 10.0, 30.0, 100.0)


@dataclass(frozen=True)
class TrainedTarget:
    """Один обученный pipeline + лучшая alpha + метрики на test-split."""

    target: str
    pipeline: Pipeline
    best_alpha: float
    test_metrics_dict: dict[str, float]


def _build_pipeline() -> Pipeline:
    """Imputer + Scaler + Ridge.

    StandardScaler не обязателен для Ridge, но улучшает сходимость и
    делает значения коэффициентов сопоставимыми (полезно для feature
    importance в дипломной главе).
    """
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("ridge", Ridge(alpha=1.0, random_state=42)),
        ]
    )


def _drop_nan_target(
    X: pd.DataFrame, y: pd.Series, groups: pd.Series
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Убрать строки, где сам target = NaN (например, muscle_mass_kg
    отсутствует у анкера). Без этого sklearn ругается."""
    mask = y.notna()
    return X.loc[mask], y.loc[mask], groups.loc[mask]


def _fit_one_target(
    *,
    target: str,
    train: DatasetSplit,
    val: DatasetSplit,
    test: DatasetSplit,
) -> TrainedTarget:
    """Подобрать alpha по GroupKFold(train+val) и протестировать на test."""
    # Объединяем train и val для CV-подбора (классический подход когда
    # хочется максимально использовать данные); test нетронут.
    X_dev = pd.concat([train.X[list(FEATURE_COLUMNS)], val.X[list(FEATURE_COLUMNS)]])
    y_dev = pd.concat([train.y[target], val.y[target]])
    g_dev = pd.concat([train.group, val.group])
    X_dev, y_dev, g_dev = _drop_nan_target(X_dev, y_dev, g_dev)

    pipeline = _build_pipeline()
    # Число fold'ов выбираем динамически: при маленьком датасете 5 групп
    # может быть недостаточно — возьмём min(5, n_groups).
    n_groups = g_dev.nunique()
    n_splits = max(2, min(5, n_groups - 1)) if n_groups > 2 else 2
    cv = GroupKFold(n_splits=n_splits)
    grid = GridSearchCV(
        pipeline,
        param_grid={"ridge__alpha": list(ALPHA_GRID)},
        cv=cv,
        scoring="neg_mean_absolute_error",
        n_jobs=1,
    )
    grid.fit(X_dev, y_dev, groups=g_dev)
    best = grid.best_estimator_
    best_alpha = float(grid.best_params_["ridge__alpha"])

    # Test metrics — на нетронутом сплите.
    X_test = test.X[list(FEATURE_COLUMNS)]
    y_test = test.y[target]
    y_pred = best.predict(X_test)
    metrics = compute_metrics(y_true=y_test, y_pred=np.asarray(y_pred))

    return TrainedTarget(
        target=target,
        pipeline=best,
        best_alpha=best_alpha,
        test_metrics_dict=metrics.to_dict(),
    )


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
    hyperparams: dict[str, float] = {}

    for target in PREDICT_TARGETS:
        result = _fit_one_target(
            target=target,
            train=splits["train"],
            val=splits["val"],
            test=splits["test"],
        )
        joblib.dump(result.pipeline, out_dir / f"{target}.joblib")
        metrics_block[target] = result.test_metrics_dict
        hyperparams[f"alpha_{target}"] = result.best_alpha

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
        hyperparams=hyperparams,
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train Ridge baseline (spec 008)")
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
        print(f"  {target}: MAE={m['mae']:.4f}  RMSE={m['rmse']:.4f}  R²={m['r2']:.3f}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
