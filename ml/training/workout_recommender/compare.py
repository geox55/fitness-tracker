"""Сравнение моделей recommender'а — для главы Егора."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .manifest import read_manifest

MODELS_ORDER = ("popularity", "lr", "lgbm", "mlp")


def render_markdown(*, root: Path, version: str) -> str:
    rows: list[str] = [
        "| model | ROC-AUC | PR-AUC | P@K | R@K |",
        "|-------|---------|--------|-----|-----|",
    ]
    for model in MODELS_ORDER:
        d = root / model / f"v{version}"
        if not (d / "manifest.json").exists():
            rows.append(f"| {model} | — | — | — | — |  *(not trained)* |")
            continue
        m = read_manifest(d)
        rows.append(
            f"| {model} | {m.metrics.get('roc_auc', 0):.3f} | "
            f"{m.metrics.get('pr_auc', 0):.3f} | "
            f"{m.metrics.get('precision_at_k', 0):.3f} | "
            f"{m.metrics.get('recall_at_k', 0):.3f} |"
        )
    return "\n".join(rows)


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare recommender models")
    parser.add_argument(
        "--root", type=Path, default=Path("ml/models/workout_rec")
    )
    parser.add_argument("--version", type=str, default="0.1.0")
    args = parser.parse_args(argv)
    print(render_markdown(root=args.root, version=args.version))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
