"""End-to-end smoke-тест training pipeline для InBody-предиктора.

Доказывает, что пайплайн работает целиком — от ETL до сохранённого
artifact + manifest:
- генерируем мини-датасет (через тот же `ml.etl.inbody.synthesize` flow,
  что в проде, но на synthetic anchors);
- запускаем `train_persistence` / `train_ridge` / `train_lgbm`;
- проверяем что artifact'ы сохранились и manifest читаемый.

Тест помечен как `unit`, но «честнее» сказать integration-style: мы
тренируем настоящие модели на крошечном датасете. Это занимает <2с в CI,
и единственное, что заменяет реальную работу с Kaggle CSV — синтетика
anchors. Если завтра появится реальный CSV — просто запустим эту же
функцию на нём.
"""

from __future__ import annotations

import csv
import random
from collections.abc import Iterable
from pathlib import Path

import pytest
from ml.etl.inbody.anchor import Anchor
from ml.etl.inbody.build import build_rows


def _synthetic_anchors(n: int, seed: int = 42) -> list[Anchor]:
    """Простые синтетические anchor'ы для smoke-теста: фиксированное seed,
    разнообразие sex/goal/возраста, реалистичные диапазоны."""
    rng = random.Random(seed)
    anchors: list[Anchor] = []
    goals = ("weight_loss", "muscle_gain", "maintenance")
    for i in range(n):
        sex = "male" if i % 2 == 0 else "female"
        age = rng.randint(20, 55)
        height = rng.uniform(160.0, 195.0) if sex == "male" else rng.uniform(150.0, 178.0)
        weight = rng.uniform(60.0, 100.0) if sex == "male" else rng.uniform(48.0, 85.0)
        bf = rng.uniform(12.0, 28.0) if sex == "male" else rng.uniform(20.0, 36.0)
        anchors.append(
            Anchor(
                raw_user_id=f"smoke-{i}",
                source="s3",
                sex=sex,  # type: ignore[arg-type]
                age_years=age,
                height_cm=height,
                weight_kg=weight,
                body_fat_percent=bf,
                muscle_mass_kg=None,
                training_frequency_per_week=rng.randint(2, 5),
                goal=goals[i % len(goals)],  # type: ignore[arg-type]
            )
        )
    return anchors


def _write_csv(rows: Iterable[tuple[object, str]], dest: Path) -> int:
    """Записать (WeekRow, split) → CSV в схеме Dataset-B (см. dataset_card.md)."""
    materialized = list(rows)
    fields = [
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
    ]
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for week, split in materialized:
            d = {**week.__dict__, "split": split}
            writer.writerow(d)
    return len(materialized)


@pytest.fixture
def mini_dataset(tmp_path: Path) -> Path:
    """40 пользователей × 8 недель = 320 строк — хватает для group-CV
    с min_data_in_leaf=20 и group-3-fold."""
    anchors = _synthetic_anchors(40)
    rows = build_rows(anchors, weeks=8, seed=42, salt="smoke")
    csv_path = tmp_path / "dataset_b_smoke.csv"
    n = _write_csv(rows, csv_path)
    assert n > 100, f"Expected >100 rows for stable CV, got {n}"
    return csv_path


class TestTrainingPipeline:
    def test_persistence_baseline(self, mini_dataset: Path, tmp_path: Path) -> None:
        from ml.training.inbody_timeseries.persistence import train

        manifest = train(
            dataset_csv=mini_dataset, out_root=tmp_path / "models", version="0.0.1-smoke"
        )

        # Persistence — Δ=0; на синтетике с трендом MAE будет нетривиальный.
        assert "delta_weight_kg" in manifest.metrics
        m = manifest.metrics["delta_weight_kg"]
        assert m["mae"] >= 0.0
        # Баум, что rmse ≥ mae (sanity).
        assert m["rmse"] >= m["mae"]
        # CI80 не считается для persistence.
        assert "ci80_coverage" not in m

    def test_ridge_baseline(self, mini_dataset: Path, tmp_path: Path) -> None:
        from ml.training.inbody_timeseries.train_ridge import train

        manifest = train(
            dataset_csv=mini_dataset, out_root=tmp_path / "models", version="0.0.1-smoke"
        )

        assert manifest.has_quantiles is False
        # Все 3 target обучились.
        assert set(manifest.metrics) == {
            "delta_weight_kg",
            "delta_body_fat_percent",
            "delta_muscle_mass_kg",
        }
        # Артефакты сохранились.
        model_dir = tmp_path / "models" / "ridge" / "v0.0.1-smoke"
        assert (model_dir / "manifest.json").exists()
        assert (model_dir / "delta_weight_kg.joblib").exists()
        assert (model_dir / "delta_body_fat_percent.joblib").exists()
        # Hyperparams содержит alpha по каждому target — следствие GridSearchCV.
        for tgt in manifest.targets:
            assert f"alpha_{tgt}" in manifest.hyperparams

    def test_lgbm_quantile(self, mini_dataset: Path, tmp_path: Path) -> None:
        from ml.training.inbody_timeseries.train_lgbm import train

        manifest = train(
            dataset_csv=mini_dataset, out_root=tmp_path / "models", version="0.0.1-smoke"
        )

        assert manifest.has_quantiles is True
        assert tuple(manifest.quantiles) == (0.10, 0.50, 0.90)

        # На каждый target — три файла (q10, q50, q90).
        model_dir = tmp_path / "models" / "lgbm" / "v0.0.1-smoke"
        for target in manifest.targets:
            for q in ("q10", "q50", "q90"):
                assert (model_dir / f"{target}_{q}.joblib").exists()

        # CI coverage должна быть посчитана для каждой метрики.
        for m in manifest.metrics.values():
            assert "ci80_coverage" in m
            # Для калиброванной модели coverage близко к 0.80.
            # На smoke-датасете допуск шире — главное, что значение в [0..1].
            assert 0.0 <= m["ci80_coverage"] <= 1.0

    def test_compare_renders_table(self, mini_dataset: Path, tmp_path: Path) -> None:
        # Тренируем классические модели (persistence/ridge/lgbm); MLP сюда не
        # добавляем — torch-обучение медленное для smoke-теста, а сам compare
        # уже умеет рендерить «not trained»-строку для отсутствующих манифестов.
        from ml.training.inbody_timeseries.compare import render_markdown
        from ml.training.inbody_timeseries.persistence import train as train_p
        from ml.training.inbody_timeseries.train_lgbm import train as train_lgbm
        from ml.training.inbody_timeseries.train_ridge import train as train_ridge

        out = tmp_path / "models"
        for fn in (train_p, train_ridge, train_lgbm):
            fn(dataset_csv=mini_dataset, out_root=out, version="0.0.1-smoke")

        table = render_markdown(root=out, version="0.0.1-smoke")
        # 3 обученные модели × 3 target = 9 строк + 1 строка-заглушка для mlp
        # + 2 строки шапки = 12.
        lines = [line for line in table.splitlines() if line.startswith("|")]
        assert len(lines) == 12
        # Все имена моделей и target'ов должны встречаться.
        assert "persistence" in table
        assert "ridge" in table
        assert "lgbm" in table
        assert "mlp" in table  # «not trained» строка
        assert "delta_weight_kg" in table
