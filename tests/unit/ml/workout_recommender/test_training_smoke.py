"""Smoke-test: ETL Dataset-C → train all → metrics → compare-table.

Аналог inbody-timeseries smoke. Использует синтетические anchors из
тестов inbody_timeseries (один и тот же шаблон), маленький фейковый
каталог из 30 упражнений и 40 user'ов.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest
from ml.etl.inbody.anchor import Anchor
from ml.etl.workout_recommender.build import run as build_dataset_c


def _synthetic_anchors(n: int, seed: int = 42) -> list[Anchor]:
    rng = random.Random(seed)
    goals = ("weight_loss", "muscle_gain", "maintenance")
    out: list[Anchor] = []
    for i in range(n):
        sex = "male" if i % 2 == 0 else "female"
        out.append(
            Anchor(
                raw_user_id=f"smoke-{i}",
                source="s3",
                sex=sex,  # type: ignore[arg-type]
                age_years=rng.randint(20, 55),
                height_cm=rng.uniform(160, 195) if sex == "male" else rng.uniform(150, 178),
                weight_kg=rng.uniform(60, 100) if sex == "male" else rng.uniform(48, 85),
                body_fat_percent=rng.uniform(12, 28) if sex == "male" else rng.uniform(20, 36),
                muscle_mass_kg=None,
                training_frequency_per_week=rng.randint(2, 5),
                goal=goals[i % len(goals)],  # type: ignore[arg-type]
                training_level=("beginner", "intermediate", "advanced")[i % 3],  # type: ignore[arg-type]
            )
        )
    return out


def _fake_catalog(n: int) -> list[dict[str, object]]:
    """30 упражнений с разнообразием групп/региона/equipment.
    Хватает, чтобы LGBM получил sample size, и хватает группы priority
    в каждой goal-категории."""
    groups = ("chest", "back", "quads", "shoulders", "abs", "biceps")
    regions = ("upper", "lower", "core")
    equip = (
        ["barbell"],
        ["dumbbell"],
        ["machine"],
        ["bodyweight"],
        ["pullup_bar"],
    )
    catalog: list[dict[str, object]] = []
    for i in range(n):
        catalog.append(
            {
                "exercise_id": f"ex_{i}",
                "exercise_name": f"Exercise {i}",
                "primary_muscle_group": groups[i % len(groups)],
                "secondary_muscle_group": [],
                "equipment": equip[i % len(equip)],
                "body_region": regions[i % len(regions)],
                # Каждое 7-е помечаем deadlift'ом — попадёт в advanced-keywords.
                "instructions": "deadlift" if i % 7 == 0 else "regular movement",
            }
        )
    # Помечаем «advanced» по name тоже — у нас в эвристике ловля по name.
    for i, ex in enumerate(catalog):
        if i % 7 == 0:
            ex["exercise_name"] = "Deadlift Variant"
    return catalog


@pytest.fixture
def mini_dataset_c(tmp_path: Path) -> Path:
    anchors = _synthetic_anchors(40)
    cat_path = tmp_path / "catalog.json"
    cat_path.write_text(
        json.dumps(_fake_catalog(30), ensure_ascii=False), encoding="utf-8"
    )
    stats = build_dataset_c(
        anchors=anchors,
        catalog_path=cat_path,
        out_dir=tmp_path,
        seed=42,
        salt="smoke",
        per_user_exercises=30,
    )
    csv_path = tmp_path / "dataset_c_workout_recommender.csv"
    assert stats["rows"] >= 100, f"too few rows: {stats}"
    return csv_path


class TestRecommenderPipeline:
    def test_popularity_baseline(
        self, mini_dataset_c: Path, tmp_path: Path
    ) -> None:
        from ml.training.workout_recommender.popularity import train

        m = train(
            dataset_csv=mini_dataset_c,
            out_root=tmp_path / "models",
            version="0.0.1-smoke",
        )
        # Constant predictor → ROC-AUC ≈ 0.5 (сравнение пар одного скора).
        assert 0.4 <= m.metrics["roc_auc"] <= 0.6
        assert m.metrics["precision_at_k"] >= 0

    def test_lr_baseline(self, mini_dataset_c: Path, tmp_path: Path) -> None:
        from ml.training.workout_recommender.train_lr import train

        m = train(
            dataset_csv=mini_dataset_c,
            out_root=tmp_path / "models",
            version="0.0.1-smoke",
        )
        # LR должен бить popularity на любом нелинейном датасете.
        assert m.metrics["roc_auc"] > 0.7
        # Артефакт сохранился.
        assert (tmp_path / "models/lr/v0.0.1-smoke/lr.joblib").exists()

    def test_lgbm_recommender(
        self, mini_dataset_c: Path, tmp_path: Path
    ) -> None:
        from ml.training.workout_recommender.train_lgbm import train

        m = train(
            dataset_csv=mini_dataset_c,
            out_root=tmp_path / "models",
            version="0.0.1-smoke",
        )
        # На smoke-датасете требования мягче: главное чтобы модель выучилась.
        assert m.metrics["roc_auc"] > 0.7
        # P@K в [0, 1].
        assert 0 <= m.metrics["precision_at_k"] <= 1
        assert (tmp_path / "models/lgbm/v0.0.1-smoke/lgbm.joblib").exists()

    def test_compare_table(self, mini_dataset_c: Path, tmp_path: Path) -> None:
        from ml.training.workout_recommender.compare import render_markdown
        from ml.training.workout_recommender.popularity import (
            train as train_pop,
        )
        from ml.training.workout_recommender.train_lgbm import (
            train as train_lgbm,
        )
        from ml.training.workout_recommender.train_lr import (
            train as train_lr,
        )

        out = tmp_path / "models"
        for fn in (train_pop, train_lr, train_lgbm):
            fn(
                dataset_csv=mini_dataset_c,
                out_root=out,
                version="0.0.1-smoke",
            )
        table = render_markdown(root=out, version="0.0.1-smoke")
        # 3 модели + header + separator = 5 строк.
        assert table.count("\n") == 4
        assert "popularity" in table
        assert "lr" in table
        assert "lgbm" in table
