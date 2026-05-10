"""Сводная таблица «модель × target × метрика» — для главы диплома.

Читает manifest.json всех трёх моделей и печатает плоскую markdown-таблицу:

| model       | target                   | MAE   | RMSE  | R²    | CI80  |
|-------------|--------------------------|-------|-------|-------|-------|
| persistence | delta_weight_kg          | 0.51  | 0.65  | 0.00  | —     |
| ridge       | delta_weight_kg          | 0.42  | 0.55  | 0.34  | —     |
| lgbm        | delta_weight_kg          | 0.38  | 0.51  | 0.42  | 0.81  |
| ...         |                          |       |       |       |       |

Эту таблицу можно вставить прямо в магистерскую работу.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .manifest import read_manifest

MODELS_ORDER = ("persistence", "ridge", "lgbm")
TARGETS_ORDER = (
    "delta_weight_kg",
    "delta_body_fat_percent",
    "delta_muscle_mass_kg",
)


def render_markdown(*, root: Path, version: str) -> str:
    rows: list[str] = []
    rows.append("| model | target | MAE | RMSE | R² | CI80 |")
    rows.append("|-------|--------|-----|------|----|------|")

    for model in MODELS_ORDER:
        manifest_dir = root / model / f"v{version}"
        if not (manifest_dir / "manifest.json").exists():
            rows.append(
                f"| {model} | (model not trained — `manifest.json` missing in "
                f"`{manifest_dir}`) | — | — | — | — |"
            )
            continue
        manifest = read_manifest(manifest_dir)
        for target in TARGETS_ORDER:
            m = manifest.metrics.get(target, {})
            ci = m.get("ci80_coverage")
            ci_cell = f"{ci:.2f}" if ci is not None else "—"
            rows.append(
                f"| {model} | {target} | "
                f"{m.get('mae', float('nan')):.4f} | "
                f"{m.get('rmse', float('nan')):.4f} | "
                f"{m.get('r2', float('nan')):.3f} | "
                f"{ci_cell} |"
            )
    return "\n".join(rows)


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare models for inbody_timeseries (markdown table)"
    )
    parser.add_argument(
        "--root", type=Path, default=Path("ml/models/inbody_pred")
    )
    parser.add_argument("--version", type=str, default="0.1.0")
    args = parser.parse_args(argv)
    print(render_markdown(root=args.root, version=args.version))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli())
