"""MLP-recommender — нейросетевая модель для главы 5 диплома Егора.

Архитектура: feed-forward MLP с двумя скрытыми слоями (128 → 64), ReLU,
Dropout, и сигмоидным выходом. Функция потерь — Binary Cross-Entropy с
весом класса (positives ~67% → лёгкое взвешивание negatives, как у LGBM
`is_unbalance=True`).

Зачем нейросеть, если LightGBM уже даёт ROC-AUC 0.98? — для диплома по
«Прикладной математике и информатике» сравнение классики и нейросетей
является обязательной частью эксперимента. Ожидаемый результат: MLP даёт
сопоставимое или чуть худшее качество, чем GBDT (типичная картина на
табличных данных), но позволяет показать корректное сравнение
архитектур (см. compare.py).

Реализация выполнена строго на тех же фичах и сплитах, что и LGBM —
любые различия в метриках объясняются только архитектурой модели.

Артефакт: ml/models/workout_rec/mlp/v{semver}/mlp.pt (state_dict + scaler).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from .data import load_dataset_c, split_dataset
from .evaluate import DEFAULT_K, compute_metrics
from .manifest import ModelManifest, model_dir, now_iso, sha256_file, write_manifest

MODEL_NAME = "mlp"
DEFAULT_VERSION = "0.1.0"

# Гиперпараметры. Подобраны под датасет ~80k строк × 36 фичей: модель
# должна быть достаточно ёмкой, чтобы поймать нелинейности, но не слишком
# (иначе быстро переобучится на rule-based разметке).
HIDDEN_DIMS = (128, 64)
DROPOUT = 0.30
LR = 1e-3
WEIGHT_DECAY = 1e-5
BATCH_SIZE = 1024
MAX_EPOCHS = 50
EARLY_STOPPING_PATIENCE = 5
SEED = 42


def _device() -> torch.device:
    """Выбор устройства: MPS на M-серии Apple, CUDA если доступна, иначе CPU.

    MPS даёт ~3x ускорение для нашей сетки vs CPU; в продакшене это
    непринципиально (предсказание — единичные строки), но обучение
    переживёт цикл из 50 эпох за секунды вместо минут.
    """
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


@dataclass(frozen=True)
class TrainHistory:
    """История обучения — для построения learning curves в дипломе."""

    train_loss: list[float]
    val_loss: list[float]
    val_pr_auc: list[float]
    best_epoch: int


class MLPClassifier(nn.Module):
    """MLP: input → 128 → ReLU → Dropout → 64 → ReLU → Dropout → 1 (sigmoid).

    Sigmoid вынесен в forward через `torch.sigmoid` (а не как часть
    Sequential), чтобы при обучении использовать `BCEWithLogitsLoss`
    (численно стабильнее), а для предсказания применять sigmoid руками.
    """

    def __init__(self, *, input_dim: int, hidden_dims: tuple[int, ...] = HIDDEN_DIMS,
                 dropout: float = DROPOUT) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = input_dim
        for h in hidden_dims:
            layers.extend([nn.Linear(prev, h), nn.ReLU(inplace=True), nn.Dropout(dropout)])
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)  # logits, shape (B,)


def _make_loader(
    *, X: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool
) -> DataLoader:
    ds = TensorDataset(
        torch.from_numpy(X.astype(np.float32)),
        torch.from_numpy(y.astype(np.float32)),
    )
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, drop_last=False)


def _epoch_pass(
    *,
    model: nn.Module,
    loader: DataLoader,
    loss_fn: nn.Module,
    optimizer: torch.optim.Optimizer | None,
    device: torch.device,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Один проход по loader'у. Если optimizer задан — обучение, иначе eval.

    Возвращает: среднюю loss, сконкатенированные скоры и метки для метрик.
    """
    is_train = optimizer is not None
    model.train(is_train)
    total_loss = 0.0
    total_n = 0
    scores: list[np.ndarray] = []
    labels: list[np.ndarray] = []

    for xb, yb in loader:
        xb = xb.to(device)
        yb = yb.to(device)
        logits = model(xb)
        loss = loss_fn(logits, yb)
        if is_train:
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        total_loss += float(loss.item()) * xb.size(0)
        total_n += xb.size(0)
        with torch.no_grad():
            scores.append(torch.sigmoid(logits).detach().cpu().numpy())
            labels.append(yb.detach().cpu().numpy())

    return total_loss / max(total_n, 1), np.concatenate(scores), np.concatenate(labels)


def _train_loop(
    *,
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    loss_fn: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> TrainHistory:
    """Цикл обучения с ранней остановкой по val PR-AUC.

    PR-AUC, а не val loss — потому что bal accuracy наша задача нестрого
    бинарная (positives ~67%), и PR-AUC более стабильная метрика для
    early stopping в imbalanced-сценарии (Saito & Rehmsmeier, 2015).
    """
    from sklearn.metrics import average_precision_score

    history_train_loss: list[float] = []
    history_val_loss: list[float] = []
    history_val_pr_auc: list[float] = []

    best_pr_auc = -1.0
    best_epoch = -1
    best_state: dict | None = None
    patience = 0

    for epoch in range(1, MAX_EPOCHS + 1):
        train_loss, _, _ = _epoch_pass(
            model=model, loader=train_loader, loss_fn=loss_fn,
            optimizer=optimizer, device=device,
        )
        val_loss, val_scores, val_labels = _epoch_pass(
            model=model, loader=val_loader, loss_fn=loss_fn,
            optimizer=None, device=device,
        )
        val_pr_auc = float(average_precision_score(val_labels, val_scores))

        history_train_loss.append(train_loss)
        history_val_loss.append(val_loss)
        history_val_pr_auc.append(val_pr_auc)

        if val_pr_auc > best_pr_auc:
            best_pr_auc = val_pr_auc
            best_epoch = epoch
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            patience = 0
        else:
            patience += 1
            if patience >= EARLY_STOPPING_PATIENCE:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    return TrainHistory(
        train_loss=history_train_loss,
        val_loss=history_val_loss,
        val_pr_auc=history_val_pr_auc,
        best_epoch=best_epoch,
    )


def train(
    *,
    dataset_csv: Path,
    out_root: Path,
    version: str = DEFAULT_VERSION,
) -> ModelManifest:
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    device = _device()

    df = load_dataset_c(dataset_csv)
    splits = split_dataset(df)
    train_split = splits["train"]
    val_split = splits["val"]
    test_split = splits["test"]

    feature_cols = list(train_split.X.columns)
    input_dim = len(feature_cols)

    # StandardScaler фитится только по train — обязательно, иначе утечка
    # из val/test в нормализацию.
    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_split.X.to_numpy())
    X_val = scaler.transform(val_split.X.to_numpy())
    X_test = scaler.transform(test_split.X.to_numpy())
    y_train = train_split.y.to_numpy()
    y_val = val_split.y.to_numpy()
    y_test = test_split.y.to_numpy()

    # Вес positive-класса. positives ~67% → pos_weight < 1, что слегка
    # «штрафует» уверенные positives. Аналог LGBM is_unbalance=True.
    pos_weight = float((1.0 - y_train.mean()) / max(y_train.mean(), 1e-9))

    model = MLPClassifier(input_dim=input_dim).to(device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight, device=device))
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    train_loader = _make_loader(X=X_train, y=y_train, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = _make_loader(X=X_val, y=y_val, batch_size=BATCH_SIZE, shuffle=False)

    history = _train_loop(
        model=model, train_loader=train_loader, val_loader=val_loader,
        loss_fn=loss_fn, optimizer=optimizer, device=device,
    )

    # Финальный inference на test
    test_loader = _make_loader(X=X_test, y=y_test, batch_size=BATCH_SIZE, shuffle=False)
    _, test_scores, _ = _epoch_pass(
        model=model, loader=test_loader, loss_fn=loss_fn, optimizer=None, device=device,
    )
    metrics = compute_metrics(
        y_true=test_split.y, y_score=test_scores, groups=test_split.group, k=DEFAULT_K,
    )

    # Сохранение артефактов: state_dict, scaler, feature_columns в одном .pt
    out_dir = model_dir(root=out_root, model_name=MODEL_NAME, version=version)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "feature_columns": feature_cols,
            "scaler_mean": scaler.mean_.tolist(),
            "scaler_scale": scaler.scale_.tolist(),
            "hidden_dims": list(HIDDEN_DIMS),
            "dropout": DROPOUT,
        },
        out_dir / f"{MODEL_NAME}.pt",
    )
    # История обучения — для построения learning curves в дипломе.
    (out_dir / "train_history.json").write_text(
        json.dumps(
            {
                "train_loss": history.train_loss,
                "val_loss": history.val_loss,
                "val_pr_auc": history.val_pr_auc,
                "best_epoch": history.best_epoch,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest = ModelManifest(
        model_name=MODEL_NAME,
        model_version=f"workout-rec-{MODEL_NAME}-{version}",
        feature_columns=feature_cols,
        dataset_sha256=sha256_file(dataset_csv),
        dataset_rows=len(df),
        dataset_positive_ratio=float(df["label"].mean()),
        trained_at=now_iso(),
        metrics=metrics.to_dict(),
        hyperparams={
            "architecture": "MLP",
            "hidden_dims": list(HIDDEN_DIMS),
            "dropout": DROPOUT,
            "learning_rate": LR,
            "weight_decay": WEIGHT_DECAY,
            "batch_size": BATCH_SIZE,
            "max_epochs": MAX_EPOCHS,
            "early_stopping_patience": EARLY_STOPPING_PATIENCE,
            "pos_weight": pos_weight,
            "best_epoch": history.best_epoch,
            "device": str(device),
            "seed": SEED,
        },
    )
    write_manifest(out_dir, manifest)
    return manifest


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MLP recommender (PyTorch)")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, default=Path("ml/models/workout_rec"))
    parser.add_argument("--version", type=str, default=DEFAULT_VERSION)
    args = parser.parse_args(argv)

    m = train(dataset_csv=args.dataset, out_root=args.out_root, version=args.version)
    print(f"Saved {m.model_version}")
    print(
        f"  ROC-AUC={m.metrics['roc_auc']:.3f} PR-AUC={m.metrics['pr_auc']:.3f}"
        f"  P@K={m.metrics['precision_at_k']:.3f}"
        f"  R@K={m.metrics['recall_at_k']:.3f}"
        f"  best_epoch={m.hyperparams['best_epoch']}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
