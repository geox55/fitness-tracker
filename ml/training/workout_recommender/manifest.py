"""Manifest для workout_recommender — структурно совпадает с inbody-timeseries.

Каталог модели:
    ml/models/workout_rec/{model_name}/v{semver}/
        manifest.json
        {model_name}.joblib   # один файл — одна модель (binary)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelManifest:
    model_name: str  # popularity | lr | lgbm
    model_version: str  # workout-rec-{model}-{semver}
    feature_columns: list[str]
    dataset_sha256: str = ""
    dataset_rows: int = 0
    dataset_positive_ratio: float = 0.0
    trained_at: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    hyperparams: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelManifest:
        return cls(**data)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def model_dir(*, root: Path, model_name: str, version: str) -> Path:
    return root / model_name / f"v{version}"


def write_manifest(dir_: Path, manifest: ModelManifest) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / "manifest.json").write_text(
        json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def read_manifest(dir_: Path) -> ModelManifest:
    raw = json.loads((dir_ / "manifest.json").read_text(encoding="utf-8"))
    return ModelManifest.from_dict(raw)
