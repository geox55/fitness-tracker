"""MLP с квантильной регрессией для InBody-предиктора — нейросетевая
модель для главы 5 диплома Маши.

Архитектура: одна сеть с тремя «головами», по одной на каждую целевую
переменную (Δweight, Δbf, Δmm). Каждая голова имеет три выхода —
квантили 0.1, 0.5, 0.9. Итого 9 выходов на сеть.

Функция потерь — pinball loss (она же quantile loss), суммированная по
3 целям × 3 квантилям. Это прямой аналог LightGBM с
objective='quantile', alpha=τ, но в одном дифференцируемом графе:

    L_τ(y, ŷ) = max(τ · (y − ŷ), (τ − 1) · (y − ŷ))

Технический трюк: чтобы избежать пересечения квантилей
(quantile crossing — частая проблема, когда q10 > q50), сеть выдаёт
δ-параметризацию: q50 = head(x), q10 = q50 − softplus(δ_lower),
q90 = q50 + softplus(δ_upper). softplus гарантирует положительность
смещений, что обеспечивает упорядоченность квантилей по построению.

NaN в y (бывает у muscle_mass_kg, когда anchor строки без замера)
исключаются из подсчёта loss через маскирование.

Артефакт: ml/models/inbody_pred/mlp/v{semver}/mlp.pt
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from .data import (
    FEATURE_COLUMNS,
    PREDICT_TARGETS,
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

MODEL_NAME = "mlp"
DEFAULT_VERSION = "0.1.0"
QUANTILES: tuple[float, float, float] = (0.10, 0.50, 0.90)

# Архитектура. Скрытые слои меньше, чем у workout-MLP (там 80k строк, у
# нас ~3k) — иначе быстро переобучимся. Dropout повыше для регуляризации.
SHARED_HIDDEN: tuple[int, ...] = (64, 32)
HEAD_HIDDEN: int = 16
DROPOUT = 0.30

LR = 1e-3
WEIGHT_DECAY = 1e-4
BATCH_SIZE = 256
MAX_EPOCHS = 200
EARLY_STOPPING_PATIENCE = 20  # бóльше, т.к. кривая loss осциллирует на малой выборке
SEED = 42


def _device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


@dataclass(frozen=True)
class TrainHistory:
    train_loss: list[float]
    val_loss: list[float]
    best_epoch: int


class QuantileMLP(nn.Module):
    """Общий «ствол» (shared trunk) + per-target головы с δ-параметризацией.

    - Trunk: input → 64 → ReLU → Dropout → 32 → ReLU → Dropout. Извлекает
      признаки, общие для всех таргетов (BMI, FFM, тренировочный объём
      одинаково важны для веса/жира/мышечной).
    - Per-target head: trunk_out → 16 → ReLU → 3 выхода (q50, δ_lower, δ_upper).
    - q10 = q50 − softplus(δ_lower); q90 = q50 + softplus(δ_upper).
      softplus(x) > 0 гарантирует q10 ≤ q50 ≤ q90 по построению.

    Альтернатива — независимые сети на каждый квантиль. Преимущество
    shared trunk: меньше параметров, регуляризация через multi-task,
    плюс по построению нет crossing'а квантилей.
    """

    def __init__(
        self,
        *,
        input_dim: int,
        n_targets: int,
        shared_hidden: tuple[int, ...] = SHARED_HIDDEN,
        head_hidden: int = HEAD_HIDDEN,
        dropout: float = DROPOUT,
    ) -> None:
        super().__init__()
        # Shared trunk
        layers: list[nn.Module] = []
        prev = input_dim
        for h in shared_hidden:
            layers.extend([nn.Linear(prev, h), nn.ReLU(inplace=True), nn.Dropout(dropout)])
            prev = h
        self.trunk = nn.Sequential(*layers)
        # Per-target heads. Каждая голова: trunk → head_hidden → 3 выхода.
        self.heads = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(prev, head_hidden),
                    nn.ReLU(inplace=True),
                    nn.Linear(head_hidden, 3),
                )
                for _ in range(n_targets)
            ]
        )
        self.n_targets = n_targets

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Возвращает tensor shape (B, n_targets, 3): q10, q50, q90 по таргетам."""
        z = self.trunk(x)
        outs = []
        for head in self.heads:
            raw = head(z)  # (B, 3): q50, δ_lower, δ_upper
            q50 = raw[:, 0]
            delta_lower = torch.nn.functional.softplus(raw[:, 1])
            delta_upper = torch.nn.functional.softplus(raw[:, 2])
            q10 = q50 - delta_lower
            q90 = q50 + delta_upper
            outs.append(torch.stack([q10, q50, q90], dim=-1))
        return torch.stack(outs, dim=1)  # (B, n_targets, 3)


def pinball_loss(
    *,
    preds: torch.Tensor,  # (B, n_targets, 3) [q10, q50, q90]
    targets: torch.Tensor,  # (B, n_targets)
    mask: torch.Tensor,  # (B, n_targets) — 1 если y не NaN
    quantiles: tuple[float, ...] = QUANTILES,
) -> torch.Tensor:
    """Сумма pinball loss по всем (target, quantile), нормированная на
    число валидных (не-NaN) ячеек.

    L_τ(y, ŷ) = max(τ · (y − ŷ), (τ − 1) · (y − ŷ)).
    """
    # broadcast: (B, n_targets, 3) — targets через unsqueeze
    y = targets.unsqueeze(-1)  # (B, n_targets, 1)
    diff = y - preds  # (B, n_targets, 3)
    q = torch.tensor(quantiles, dtype=preds.dtype, device=preds.device)  # (3,)
    # pinball
    loss_per = torch.maximum(q * diff, (q - 1.0) * diff)  # (B, n_targets, 3)
    # mask по таргетам (broadcast на квантили)
    m = mask.unsqueeze(-1).expand_as(loss_per)
    total = (loss_per * m).sum()
    n_valid = m.sum().clamp(min=1.0)
    return total / n_valid


def _build_tensors(
    *,
    X: pd.DataFrame,
    y: pd.DataFrame,
    feature_cols: list[str],
    target_names: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Подготовить numpy-массивы X, y, mask.

    y NaN → заменяется на 0 (значение не важно — будет замаскировано в loss).
    """
    X_arr = X[feature_cols].to_numpy()
    y_arr = y[target_names].to_numpy()
    mask = ~np.isnan(y_arr)
    y_arr = np.nan_to_num(y_arr, nan=0.0)
    return X_arr, y_arr, mask.astype(np.float32)


def _make_loader(
    *,
    X: np.ndarray,
    y: np.ndarray,
    mask: np.ndarray,
    batch_size: int,
    shuffle: bool,
) -> DataLoader:
    ds = TensorDataset(
        torch.from_numpy(X.astype(np.float32)),
        torch.from_numpy(y.astype(np.float32)),
        torch.from_numpy(mask.astype(np.float32)),
    )
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, drop_last=False)


def _epoch_pass(
    *,
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer | None,
    device: torch.device,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Один проход по loader'у. Возвращает loss и собранные prediсts/targets/mask."""
    is_train = optimizer is not None
    model.train(is_train)
    total_loss = 0.0
    total_n = 0
    preds_all: list[np.ndarray] = []
    targets_all: list[np.ndarray] = []
    masks_all: list[np.ndarray] = []

    for xb, yb, mb in loader:
        xb = xb.to(device)
        yb = yb.to(device)
        mb = mb.to(device)
        preds = model(xb)
        loss = pinball_loss(preds=preds, targets=yb, mask=mb)
        if is_train:
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        total_loss += float(loss.item()) * xb.size(0)
        total_n += xb.size(0)
        with torch.no_grad():
            preds_all.append(preds.detach().cpu().numpy())
            targets_all.append(yb.detach().cpu().numpy())
            masks_all.append(mb.detach().cpu().numpy())

    return (
        total_loss / max(total_n, 1),
        np.concatenate(preds_all, axis=0),
        np.concatenate(targets_all, axis=0),
        np.concatenate(masks_all, axis=0),
    )


def _train_loop(
    *,
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> TrainHistory:
    """Цикл обучения с early stopping по val pinball loss."""
    train_losses: list[float] = []
    val_losses: list[float] = []
    best_val = float("inf")
    best_epoch = -1
    best_state: dict | None = None
    patience = 0

    for epoch in range(1, MAX_EPOCHS + 1):
        train_loss, _, _, _ = _epoch_pass(
            model=model, loader=train_loader, optimizer=optimizer, device=device,
        )
        val_loss, _, _, _ = _epoch_pass(
            model=model, loader=val_loader, optimizer=None, device=device,
        )
        train_losses.append(train_loss)
        val_losses.append(val_loss)

        if val_loss < best_val:
            best_val = val_loss
            best_epoch = epoch
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            patience = 0
        else:
            patience += 1
            if patience >= EARLY_STOPPING_PATIENCE:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    return TrainHistory(train_loss=train_losses, val_loss=val_losses, best_epoch=best_epoch)


def train(
    *,
    dataset_csv: Path,
    out_root: Path,
    version: str = DEFAULT_VERSION,
) -> ModelManifest:
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    device = _device()

    df = load_dataset_b(dataset_csv)
    splits = split_dataset(df)
    train_split = splits["train"]
    val_split = splits["val"]
    test_split = splits["test"]

    feature_cols = list(FEATURE_COLUMNS)
    target_names = list(PREDICT_TARGETS)
    input_dim = len(feature_cols)
    n_targets = len(target_names)

    # Impute муссл массу медианой по train (как Ridge baseline).
    imputer = SimpleImputer(strategy="median")
    X_train_imp = imputer.fit_transform(train_split.X[feature_cols].to_numpy())
    X_val_imp = imputer.transform(val_split.X[feature_cols].to_numpy())
    X_test_imp = imputer.transform(test_split.X[feature_cols].to_numpy())

    # StandardScaler фитится по train.
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_imp)
    X_val = scaler.transform(X_val_imp)
    X_test = scaler.transform(X_test_imp)

    y_train = train_split.y[target_names]
    y_val = val_split.y[target_names]
    y_test = test_split.y[target_names]

    _, y_train_arr, mask_train = _build_tensors(
        X=pd.DataFrame(X_train, columns=feature_cols), y=y_train,
        feature_cols=feature_cols, target_names=target_names,
    )
    _, y_val_arr, mask_val = _build_tensors(
        X=pd.DataFrame(X_val, columns=feature_cols), y=y_val,
        feature_cols=feature_cols, target_names=target_names,
    )
    _, y_test_arr, mask_test = _build_tensors(
        X=pd.DataFrame(X_test, columns=feature_cols), y=y_test,
        feature_cols=feature_cols, target_names=target_names,
    )

    train_loader = _make_loader(X=X_train, y=y_train_arr, mask=mask_train,
                                batch_size=BATCH_SIZE, shuffle=True)
    val_loader = _make_loader(X=X_val, y=y_val_arr, mask=mask_val,
                              batch_size=BATCH_SIZE, shuffle=False)
    test_loader = _make_loader(X=X_test, y=y_test_arr, mask=mask_test,
                               batch_size=BATCH_SIZE, shuffle=False)

    model = QuantileMLP(input_dim=input_dim, n_targets=n_targets).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    history = _train_loop(
        model=model, train_loader=train_loader, val_loader=val_loader,
        optimizer=optimizer, device=device,
    )

    # Финальный inference на test.
    _, preds_test, _, _ = _epoch_pass(
        model=model, loader=test_loader, optimizer=None, device=device,
    )
    # preds_test: (N, n_targets, 3) — [q10, q50, q90]
    metrics_block: dict[str, dict[str, float]] = {}
    for i, target in enumerate(target_names):
        # Восстановим оригинальный y_test (с NaN) для совместимости с evaluate.compute_metrics,
        # которая сама дропает NaN через mask.
        y_orig = y_test[target]
        q10 = preds_test[:, i, 0]
        q50 = preds_test[:, i, 1]
        q90 = preds_test[:, i, 2]
        metrics_block[target] = compute_metrics(
            y_true=y_orig, y_pred=q50, q_low=q10, q_high=q90,
        ).to_dict()

    out_dir = model_dir(root=out_root, model_name=MODEL_NAME, version=version)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "feature_columns": feature_cols,
            "target_names": target_names,
            "quantiles": list(QUANTILES),
            "imputer_statistics": imputer.statistics_.tolist(),
            "scaler_mean": scaler.mean_.tolist(),
            "scaler_scale": scaler.scale_.tolist(),
            "shared_hidden": list(SHARED_HIDDEN),
            "head_hidden": HEAD_HIDDEN,
            "dropout": DROPOUT,
        },
        out_dir / f"{MODEL_NAME}.pt",
    )
    (out_dir / "train_history.json").write_text(
        json.dumps(
            {
                "train_loss": history.train_loss,
                "val_loss": history.val_loss,
                "best_epoch": history.best_epoch,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest = ModelManifest(
        model_name=MODEL_NAME,
        model_version=f"inbody-pred-{MODEL_NAME}-{version}",
        feature_columns=feature_cols,
        targets=target_names,
        has_quantiles=True,
        quantiles=QUANTILES,
        dataset_sha256=sha256_file(dataset_csv),
        dataset_rows=len(df),
        trained_at=now_iso(),
        metrics=metrics_block,
        hyperparams={
            "architecture": "Multi-target quantile MLP with shared trunk",
            "shared_hidden": list(SHARED_HIDDEN),
            "head_hidden": HEAD_HIDDEN,
            "dropout": DROPOUT,
            "learning_rate": LR,
            "weight_decay": WEIGHT_DECAY,
            "batch_size": BATCH_SIZE,
            "max_epochs": MAX_EPOCHS,
            "early_stopping_patience": EARLY_STOPPING_PATIENCE,
            "best_epoch": history.best_epoch,
            "device": str(device),
            "seed": SEED,
        },
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Quantile-MLP InBody predictor (PyTorch)")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, default=Path("ml/models/inbody_pred"))
    parser.add_argument("--version", type=str, default=DEFAULT_VERSION)
    args = parser.parse_args(argv)

    m = train(dataset_csv=args.dataset, out_root=args.out_root, version=args.version)
    print(f"Saved {m.model_version} (best epoch {m.hyperparams['best_epoch']})")
    for target, met in m.metrics.items():
        cov = met.get("ci80_coverage", 0.0)
        print(
            f"  {target}: MAE={met['mae']:.4f} "
            f"RMSE={met['rmse']:.4f} R²={met['r2']:.3f} CI80={cov:.2f}"
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
