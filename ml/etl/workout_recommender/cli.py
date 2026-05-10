"""CLI: build Dataset-C workout_recommender (spec 006 + 012).

Запуск:
    uv run python -m ml.etl.workout_recommender.cli \\
        --s3 ml/data/raw/gym_members_exercise.csv \\
        --s4 ml/data/raw/bodyfat.csv \\
        --catalog ml/data/processed/exercises_catalog.json \\
        --out ml/data/processed/

Источники S3/S4 — те же Kaggle CSV, что в Dataset-B; каталог упражнений
готов и закоммичен. На выход — `dataset_c_workout_recommender.csv` +
`dataset_c_workout_recommender.meta.json`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..inbody.sources import parse_s3_csv, parse_s4_csv
from .build import DEFAULT_PER_USER_EXERCISES, DEFAULT_SEED, run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build Dataset-C workout_recommender (spec 006)"
    )
    parser.add_argument("--s3", type=Path, default=None, help="S3 raw CSV")
    parser.add_argument("--s4", type=Path, default=None, help="S4 raw CSV")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("ml/data/processed/exercises_catalog.json"),
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="Output directory"
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--salt", type=str, default="fitness-tracker-thesis")
    parser.add_argument(
        "--per-user", type=int, default=DEFAULT_PER_USER_EXERCISES
    )
    args = parser.parse_args(argv)

    if args.s3 is None and args.s4 is None:
        parser.error("at least one of --s3 / --s4 is required")

    anchors = []
    if args.s3 is not None:
        anchors.extend(parse_s3_csv(args.s3))
    if args.s4 is not None:
        anchors.extend(parse_s4_csv(args.s4))

    stats = run(
        anchors=anchors,
        catalog_path=args.catalog,
        out_dir=args.out,
        seed=args.seed,
        salt=args.salt,
        per_user_exercises=args.per_user,
    )
    print(
        f"Built {stats['rows']} rows ({stats['positives']} positives, "
        f"{stats['positive_ratio']*100:.1f}%); "
        f"{stats['excluded_by_equipment']} excluded by equipment"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
