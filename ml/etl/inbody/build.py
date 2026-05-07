"""Главный entry point ETL для Dataset-B inbody_timeseries.

Pipeline:
    raw CSV (S3, S4)
      → parse_s3_csv / parse_s4_csv → list[Anchor]
      → impute.filter_and_impute (outliers + BMR)
      → synthesize_trajectory (на каждый anchor)
      → anonymize_user_id
      → split_users (70/15/15)
      → CSV writer

Воспроизводимость (REQ-20):
- Все источники случайности идут через переданный seed (random.Random(seed)).
- На вход логируем sha256 каждого raw-файла.
- На выход пишем dataset_meta.json: версия, seed, hash источников, счётчики.
"""

from __future__ import annotations

import csv
import dataclasses
import hashlib
import json
import random
from datetime import UTC, datetime
from pathlib import Path

from .anchor import Anchor
from .anonymize import anon_user_id
from .impute import filter_and_impute
from .sources import parse_s3_csv, parse_s4_csv
from .split import assert_no_leakage, assign_split
from .synthesize import WeekRow, synthesize_trajectory

DATASET_VERSION = "0.1.0"
DEFAULT_WEEKS = 8
DEFAULT_SEED = 42


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_anchors(
    *,
    s3_path: Path | None,
    s4_path: Path | None,
) -> list[Anchor]:
    anchors: list[Anchor] = []
    if s3_path is not None:
        anchors.extend(parse_s3_csv(s3_path))
    if s4_path is not None:
        anchors.extend(parse_s4_csv(s4_path))
    return anchors


def build_rows(
    anchors: list[Anchor],
    *,
    weeks: int,
    seed: int,
    salt: str,
) -> list[tuple[WeekRow, str]]:
    """Anchor-list → синтезированные строки + split.

    Это **чистая функция** — никакого I/O. Тестируется юнит-тестами
    подачей готовых анкеров.
    """
    clean, _stats = filter_and_impute(anchors)
    rng = random.Random(seed)

    all_rows: list[WeekRow] = []
    for anchor in clean:
        anon_id = anon_user_id(anchor.raw_user_id, salt=salt)
        all_rows.extend(
            synthesize_trajectory(
                anchor, anon_user_id=anon_id, weeks=weeks, rng=rng
            )
        )

    paired = assign_split(all_rows, seed=seed)
    assert_no_leakage(paired)
    return paired


# ---- Writers ---------------------------------------------------------------


_FIELDS = (
    "anon_user_id",
    "t_week",
    "age",
    "sex",
    "height_cm",
    "weight_kg",
    "body_fat_percent",
    "muscle_mass_kg",
    "training_volume_t",
    "calories_t",
    "target_weight_t1",
    "target_bf_t1",
    "target_mm_t1",
    "split",
    "is_synthetic",
)


def write_csv(paired: list[tuple[WeekRow, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDS)
        writer.writeheader()
        for row, split in paired:
            d = dataclasses.asdict(row)
            d["split"] = split
            writer.writerow(d)


def write_meta(
    *,
    out_path: Path,
    seed: int,
    salt_hash: str,
    weeks: int,
    n_rows: int,
    n_users: int,
    source_hashes: dict[str, str],
) -> None:
    meta = {
        "dataset": "inbody_timeseries",
        "version": DATASET_VERSION,
        "built_at": datetime.now(UTC).isoformat(),
        "seed": seed,
        "salt_sha256": salt_hash,
        "weeks_per_user": weeks,
        "rows": n_rows,
        "unique_users": n_users,
        "source_files": source_hashes,
        "is_synthetic": True,
    }
    out_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))


# ---- Entry ----------------------------------------------------------------


def run(
    *,
    s3_path: Path | None,
    s4_path: Path | None,
    out_dir: Path,
    weeks: int = DEFAULT_WEEKS,
    seed: int = DEFAULT_SEED,
    salt: str = "fitness-tracker-thesis",
) -> dict[str, object]:
    """Полный прогон pipeline. Возвращает статистику для логов."""
    if s3_path is None and s4_path is None:
        raise ValueError(
            "at least one of S3/S4 raw files must be provided "
            "(нет ни одного источника — генерировать нечего)"
        )

    anchors = collect_anchors(s3_path=s3_path, s4_path=s4_path)
    paired = build_rows(anchors, weeks=weeks, seed=seed, salt=salt)
    n_rows = len(paired)
    n_users = len({r.anon_user_id for r, _ in paired})

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(paired, out_dir / "dataset_b_inbody_timeseries.csv")

    source_hashes: dict[str, str] = {}
    if s3_path is not None:
        source_hashes["s3"] = _sha256(s3_path)
    if s4_path is not None:
        source_hashes["s4"] = _sha256(s4_path)
    salt_hash = hashlib.sha256(salt.encode()).hexdigest()
    write_meta(
        out_path=out_dir / "dataset_b_inbody_timeseries.meta.json",
        seed=seed,
        salt_hash=salt_hash,
        weeks=weeks,
        n_rows=n_rows,
        n_users=n_users,
        source_hashes=source_hashes,
    )
    return {
        "rows": n_rows,
        "users": n_users,
        "anchors_input": len(anchors),
    }
