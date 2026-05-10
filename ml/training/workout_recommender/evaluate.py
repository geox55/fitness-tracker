"""Метрики качества рекомендатора.

ROC-AUC и PR-AUC — общая способность ранжировать positives выше negatives.
Precision@K / Recall@K — критично для recommender'а: на вход «top-N
упражнений» пользователь увидит ровно K, и нам важна доля релевантных
именно среди них (не на всём ranking'е).

K берётся как «сколько упражнений показывается в плане за неделю»: 4–8.
По умолчанию K=8 (верхняя граница из spec 006 REQ-07). Считаем
group-aware: precision@K считается per-user (берём top-K скорингов
этого user'а из его test-набора), потом усредняем по users.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

DEFAULT_K = 8


@dataclass(frozen=True)
class RecMetrics:
    roc_auc: float
    pr_auc: float
    precision_at_k: float
    recall_at_k: float
    k: int = DEFAULT_K

    def to_dict(self) -> dict[str, float]:
        return {
            "roc_auc": float(self.roc_auc),
            "pr_auc": float(self.pr_auc),
            "precision_at_k": float(self.precision_at_k),
            "recall_at_k": float(self.recall_at_k),
            "k": float(self.k),
        }


def _per_user_pk_rk(
    *, y_true: np.ndarray, y_score: np.ndarray, groups: np.ndarray, k: int
) -> tuple[float, float]:
    """Усреднённый по users precision@K и recall@K.

    Если у user'а в test-сплите < K записей, K локально клампится до
    числа доступных строк. Если у user'а ноль positives — recall@K
    игнорируется (был бы 0/0 — это «нет смысла измерять для этого user'а»);
    precision считается всегда.
    """
    df = pd.DataFrame({"y": y_true, "s": y_score, "g": groups})
    p_sum, r_sum = 0.0, 0.0
    n_p, n_r = 0, 0
    for _g, sub in df.groupby("g", sort=False):
        sub_sorted = sub.sort_values("s", ascending=False)
        k_eff = min(k, len(sub_sorted))
        top = sub_sorted.head(k_eff)
        hits = int(top["y"].sum())
        # precision@K — всегда считаем (пользователь увидит K вариантов).
        p_sum += hits / k_eff
        n_p += 1
        total_positives = int(sub["y"].sum())
        if total_positives > 0:
            r_sum += hits / total_positives
            n_r += 1
    p_at_k = p_sum / n_p if n_p else 0.0
    r_at_k = r_sum / n_r if n_r else 0.0
    return p_at_k, r_at_k


def compute_metrics(
    *,
    y_true: pd.Series,
    y_score: np.ndarray,
    groups: pd.Series,
    k: int = DEFAULT_K,
) -> RecMetrics:
    yt = y_true.to_numpy()
    ys = np.asarray(y_score)
    gr = groups.to_numpy()

    # AUC undefined при single-class — fallback к 0.5 (random).
    if len(np.unique(yt)) < 2:
        roc, pr = 0.5, float(np.mean(yt))
    else:
        roc = float(roc_auc_score(yt, ys))
        pr = float(average_precision_score(yt, ys))

    p_at_k, r_at_k = _per_user_pk_rk(y_true=yt, y_score=ys, groups=gr, k=k)
    return RecMetrics(
        roc_auc=roc,
        pr_auc=pr,
        precision_at_k=p_at_k,
        recall_at_k=r_at_k,
        k=k,
    )
