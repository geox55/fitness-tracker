"""CLI-обёртка над `build.run` — spec 012 §9.

Запуск:
    uv run python -m ml.etl.inbody.cli \\
        --s3 ml/data/raw/gym_members_exercise.csv \\
        --s4 ml/data/raw/bodyfat.csv \\
        --out ml/data/processed/

Источники нужно скачать вручную с Kaggle (см. ml/data/processed/LICENSES.md
для ссылок) — мы не качаем за пользователя, чтобы не нарушить ToS.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .build import DEFAULT_SEED, DEFAULT_WEEKS, run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build Dataset-B inbody_timeseries (spec 012)"
    )
    parser.add_argument("--s3", type=Path, default=None, help="S3 raw CSV")
    parser.add_argument("--s4", type=Path, default=None, help="S4 raw CSV")
    parser.add_argument(
        "--out", type=Path, required=True, help="Output directory"
    )
    parser.add_argument("--weeks", type=int, default=DEFAULT_WEEKS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--salt",
        type=str,
        default="fitness-tracker-thesis",
        help="Anonymization salt (REQ-17). Не коммитить в репо.",
    )
    args = parser.parse_args(argv)

    if args.s3 is None and args.s4 is None:
        parser.error("at least one of --s3 / --s4 is required")

    stats = run(
        s3_path=args.s3,
        s4_path=args.s4,
        out_dir=args.out,
        weeks=args.weeks,
        seed=args.seed,
        salt=args.salt,
    )
    print(
        f"Built {stats['rows']} rows for {stats['users']} users "
        f"from {stats['anchors_input']} input anchors"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
