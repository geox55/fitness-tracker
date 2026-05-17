"""Тесты ML-ранкера workout-рекомендатора — spec 006 §2.

Чистые юниты без БД и без реального LGBM-артефакта: проверяем feature
engineering и edge cases загрузки. Сам joblib-load прогоняется только
если pyproject-группа ml установлена (см. условный skip).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.domain.workout_generator.recommender import (
    RankerExerciseFeatures,
    RankerUserFeatures,
    _build_features,
    _is_likely_advanced,
    load_ranker,
)

# ---------------------------------------------------------------------------
# Feature engineering: должно повторять ml/training/.../data.py 1:1
# ---------------------------------------------------------------------------


def _sample_user() -> RankerUserFeatures:
    return RankerUserFeatures(
        age=30,
        sex_male=1,
        height_cm=180.0,
        weight_kg=80.0,
        body_fat_percent=20.0,
        equipment_count=6,
        goal="muscle_gain",
        level="intermediate",
    )


def _sample_exercise(**kwargs: object) -> RankerExerciseFeatures:
    defaults: dict[str, object] = {
        "exercise_id": "ex-1",
        "primary_muscle_group": "chest",
        "body_region": "upper",
        "equipment": ("barbell", "bench"),
        "name": "Bench Press",
    }
    defaults.update(kwargs)
    return RankerExerciseFeatures(**defaults)  # type: ignore[arg-type]


def test_features_match_training_columns_count() -> None:
    """36 признаков: 8 user numeric + 5 exercise bool + 3 goal + 3 level +
    14 group + 3 region (см. ml/training/workout_recommender/data.py)."""
    user = _sample_user()
    ex = _sample_exercise()
    # Передаём именно тот набор колонок, в котором обучалась модель.
    feature_columns = (
        "user_age",
        "user_sex_male",
        "user_height_cm",
        "user_weight_kg",
        "user_body_fat",
        "user_bmi",
        "user_ffm",
        "user_equipment_count",
        "is_advanced",
        "needs_barbell",
        "needs_dumbbell",
        "needs_machine",
        "needs_bodyweight_only",
        "goal_weight_loss",
        "goal_muscle_gain",
        "goal_maintenance",
        "level_beginner",
        "level_intermediate",
        "level_advanced",
        "group_abs",
        "group_back",
        "group_biceps",
        "group_calves",
        "group_chest",
        "group_forearms",
        "group_glutes",
        "group_hamstrings",
        "group_lats",
        "group_lower_back",
        "group_quads",
        "group_shoulders",
        "group_traps",
        "group_triceps",
        "region_upper",
        "region_lower",
        "region_core",
    )
    feats = _build_features(user, ex, feature_columns)
    assert len(feats) == len(feature_columns) == 36


def test_features_one_hot_correct() -> None:
    """Один-hot должны выдавать ровно 1.0 для нужной категории и 0.0 для остальных."""
    user = _sample_user()
    ex = _sample_exercise(primary_muscle_group="chest", body_region="upper")

    feature_columns = (
        "goal_weight_loss",
        "goal_muscle_gain",
        "goal_maintenance",
        "level_beginner",
        "level_intermediate",
        "level_advanced",
        "group_chest",
        "group_back",
        "region_upper",
        "region_lower",
    )
    feats = _build_features(user, ex, feature_columns)
    # goal=muscle_gain
    assert feats[0] == 0.0
    assert feats[1] == 1.0
    assert feats[2] == 0.0
    # level=intermediate
    assert feats[3] == 0.0
    assert feats[4] == 1.0
    assert feats[5] == 0.0
    # group=chest
    assert feats[6] == 1.0
    assert feats[7] == 0.0
    # region=upper
    assert feats[8] == 1.0
    assert feats[9] == 0.0


def test_features_bmi_ffm_derived() -> None:
    user = _sample_user()  # 80 кг / 180 см
    ex = _sample_exercise()
    feats = _build_features(user, ex, ("user_bmi", "user_ffm"))
    # BMI = 80 / 1.8^2 ≈ 24.69
    assert feats[0] == pytest.approx(24.69, abs=0.01)
    # FFM = 80 * (1 - 20/100) = 64
    assert feats[1] == pytest.approx(64.0, abs=0.001)


def test_features_needs_bodyweight_only() -> None:
    """needs_bodyweight_only=1 если equipment ⊆ {'bodyweight'}; иначе 0."""
    user = _sample_user()
    ex_bw = _sample_exercise(equipment=("bodyweight",))
    ex_mixed = _sample_exercise(equipment=("bodyweight", "dumbbell"))
    ex_empty = _sample_exercise(equipment=())

    feats_bw = _build_features(user, ex_bw, ("needs_bodyweight_only",))
    feats_mixed = _build_features(user, ex_mixed, ("needs_bodyweight_only",))
    feats_empty = _build_features(user, ex_empty, ("needs_bodyweight_only",))

    assert feats_bw[0] == 1.0
    assert feats_mixed[0] == 0.0
    # Пустой equipment → set() ⊆ {bodyweight} → True (вырожденный случай).
    assert feats_empty[0] == 1.0


def test_features_unknown_column_returns_zero() -> None:
    """Forward-compat: если manifest когда-то добавит колонку, которую
    serve не умеет — отдаём 0.0, а не падаем."""
    user = _sample_user()
    ex = _sample_exercise()
    feats = _build_features(user, ex, ("totally_unknown_feature_42",))
    assert feats == [0.0]


# ---------------------------------------------------------------------------
# is_advanced heuristic — копия из ETL labelling.py
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("exercise_id", "name", "expected"),
    [
        ("barbell_back_squat", "Barbell Back Squat", False),
        ("deadlift", "Deadlift", True),  # ADVANCED_KEYWORDS
        ("snatch_high_pull", "Snatch High Pull", True),
        ("front_squat", "Front Squat", True),
        ("dumbbell_curl", "Dumbbell Curl", False),
        ("ex-uuid-123", "Pistol Squat", True),
    ],
)
def test_is_likely_advanced(exercise_id: str, name: str, expected: bool) -> None:
    assert _is_likely_advanced(exercise_id, name) is expected


# ---------------------------------------------------------------------------
# load_ranker: edge cases загрузки
# ---------------------------------------------------------------------------


def test_load_ranker_returns_none_for_missing_dir(tmp_path: Path) -> None:
    assert load_ranker(tmp_path / "nope") is None


def test_load_ranker_returns_none_when_no_versions(tmp_path: Path) -> None:
    (tmp_path / "not-a-version").mkdir()
    assert load_ranker(tmp_path) is None


def test_load_ranker_returns_none_when_manifest_missing(tmp_path: Path) -> None:
    (tmp_path / "v0.1.0").mkdir()
    assert load_ranker(tmp_path) is None


def test_load_ranker_returns_none_when_manifest_malformed(tmp_path: Path) -> None:
    v = tmp_path / "v0.1.0"
    v.mkdir()
    (v / "manifest.json").write_text("{not-json", encoding="utf-8")
    assert load_ranker(tmp_path) is None


def test_load_ranker_returns_none_when_feature_columns_empty(tmp_path: Path) -> None:
    v = tmp_path / "v0.1.0"
    v.mkdir()
    (v / "manifest.json").write_text(
        json.dumps({"feature_columns": [], "model_version": "x"}),
        encoding="utf-8",
    )
    assert load_ranker(tmp_path) is None


def test_load_ranker_returns_none_when_artifact_missing(tmp_path: Path) -> None:
    """Manifest ок, joblib-файла нет → None (без exception)."""
    pytest.importorskip("joblib")
    v = tmp_path / "v0.1.0"
    v.mkdir()
    (v / "manifest.json").write_text(
        json.dumps(
            {
                "feature_columns": ["user_age"],
                "model_version": "test-0.0.1",
            }
        ),
        encoding="utf-8",
    )
    assert load_ranker(tmp_path) is None


# ---------------------------------------------------------------------------
# score_exercises: smoke с реальным артефактом, если он есть на диске
# ---------------------------------------------------------------------------


def test_score_exercises_with_real_artifact_if_available() -> None:
    """Запускается только если на машине есть обученный LGBM. На CI без
    ML-группы тест автоматически skip'нется."""
    pytest.importorskip("joblib")
    pytest.importorskip("numpy")
    from app.domain.workout_generator.recommender import score_exercises

    ranker = load_ranker()
    if ranker is None:
        pytest.skip("workout-rec LGBM-артефакт не найден на диске")

    user = _sample_user()
    exercises = [
        _sample_exercise(
            exercise_id="ex-a",
            primary_muscle_group="chest",
            body_region="upper",
            equipment=("barbell", "bench"),
            name="Bench Press",
        ),
        _sample_exercise(
            exercise_id="ex-b",
            primary_muscle_group="back",
            body_region="upper",
            equipment=("bodyweight",),
            name="Pull Up",
        ),
    ]
    scores = score_exercises(ranker, user=user, exercises=exercises)
    assert set(scores.keys()) == {"ex-a", "ex-b"}
    # LGBM с objective='binary' → значения в (0, 1).
    for s in scores.values():
        assert 0.0 <= s <= 1.0
