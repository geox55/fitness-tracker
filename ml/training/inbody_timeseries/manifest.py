"""Manifest и сериализация артефактов модели.

Формат каталога модели:
    ml/models/inbody_pred/{model_name}/v{semver}/
        manifest.json     # метаданные: фичи, метрики, hash датасета
        {target}.joblib   # для ridge — один файл на target
        {target}_q{int}.joblib   # для lgbm — три файла на target (низкий/средний/высокий квантиль)

Manifest читается рантаймом (`domain/forecast/ml_predictor.py`) при старте,
артефакты — лениво по запросу. Хеш датасета пишется в манифест, чтобы
сравнивать «обучено на каком датасете» в repro-целях.
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
    """Содержимое manifest.json. Все поля сериализуемые в JSON.

    `model_version` — то же самое, что в `predictor.MODEL_VERSION_BASELINE`,
    но с другим именем модели; пишется в БД-таблицу InBodyForecast.
    `metrics` — словарь {target: {metric: value}}, например:
        {"delta_weight_kg": {"mae": 0.21, "rmse": 0.34, "r2": 0.42, "ci80_coverage": 0.81}}.
    """

    model_name: str  # "ridge" | "lgbm" | "persistence"
    model_version: str  # inbody-pred-{model_name}-{semver}
    feature_columns: list[str]
    targets: list[str]
    has_quantiles: bool  # True для lgbm: q=0.1/0.5/0.9 файлы
    quantiles: tuple[float, ...] = (0.5,)
    dataset_sha256: str = ""  # hash csv-файла датасета
    dataset_rows: int = 0
    trained_at: str = ""
    metrics: dict[str, dict[str, float]] = field(default_factory=dict)
    hyperparams: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelManifest:
        # quantiles в JSON приходит списком — конвертируем в tuple для frozen.
        if "quantiles" in data and isinstance(data["quantiles"], list):
            data = {**data, "quantiles": tuple(data["quantiles"])}
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["quantiles"] = list(self.quantiles)
        return d


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def model_dir(*, root: Path, model_name: str, version: str) -> Path:
    """Канонический путь к каталогу модели — `root/{model_name}/v{version}`.

    `root` обычно `ml/models/inbody_pred/`. Создание не делаем — это
    задача train_*.py.
    """
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
