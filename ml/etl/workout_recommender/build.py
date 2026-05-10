"""ETL Dataset-C: пары (user × exercise) → relevance label.

Pipeline:
    Anchor[] (из ml.etl.inbody.sources)
      ⨯ Catalog[] (ml/data/processed/exercises_catalog.json)
      → labelling.relevance
      → CSV (anon_user_id, user-фичи, exercise-фичи, label, score)

Воспроизводимость: принимает seed (хотя сам labelling детерминирован,
seed нужен для split на train/val/test).

Сплит делается **по user_id, без leakage** — те же 70/15/15, что в
inbody-timeseries: один и тот же пользователь не должен попасть в два
сплита, иначе модель увидит «знакомых» юзеров на тесте.
"""

from __future__ import annotations

import csv
import json
import random
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..inbody.anchor import Anchor
from ..inbody.anonymize import anon_user_id
from ..inbody.impute import filter_and_impute
from ..inbody.split import split_users
from .labelling import (
    ExerciseContext,
    RelevanceScore,
    UserContext,
    is_likely_advanced,
    relevance,
)

DATASET_VERSION = "0.1.0"
DEFAULT_SEED = 42
# Для каждого пользователя сэмплим N упражнений. На полном каталоге (873)
# обучающий фрейм был бы 1М строк — это и для LGBM, и для S3-anchors
# непропорционально много, и переобучение растёт. Берём ~80, чтобы покрытие
# каждой группы мышц было репрезентативным, но размер оставался
# управляемым (≈ 1000 users × 80 = 80k строк).
DEFAULT_PER_USER_EXERCISES = 80


@dataclass(frozen=True)
class _CatalogExercise:
    exercise_id: str
    exercise_name: str
    primary_muscle_group: str
    secondary_muscle_groups: tuple[str, ...]
    equipment: tuple[str, ...]
    body_region: str

    def to_context(self) -> ExerciseContext:
        return ExerciseContext(
            exercise_id=self.exercise_id,
            primary_muscle_group=self.primary_muscle_group,
            secondary_muscle_groups=self.secondary_muscle_groups,
            equipment=self.equipment,
            body_region=self.body_region,
            is_advanced=is_likely_advanced(self.exercise_id, self.exercise_name),
        )


def load_catalog(path: Path) -> list[_CatalogExercise]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: list[_CatalogExercise] = []
    for item in raw:
        sec_raw = item.get("secondary_muscle_group", []) or []
        # В каталоге secondary может быть list или строка — нормализуем.
        sec = (
            ((sec_raw,) if sec_raw else ())
            if isinstance(sec_raw, str)
            else tuple(sec_raw)
        )
        out.append(
            _CatalogExercise(
                exercise_id=item["exercise_id"],
                exercise_name=item.get("exercise_name", ""),
                primary_muscle_group=item.get("primary_muscle_group", ""),
                secondary_muscle_groups=sec,
                equipment=tuple(item.get("equipment", []) or ()),
                body_region=item.get("body_region", ""),
            )
        )
    return out


def _anchor_to_user_context(
    anchor: Anchor, *, equipment_available: tuple[str, ...]
) -> UserContext:
    """Anchor.goal может быть None (S4 не содержит цели) — для labelling
    подбираем по эвристике, той же, что в `synthesize._infer_goal`.

    Этот блок дублирует логику synthesize'а намеренно: ETL-пайплайны
    инициализируются независимо, и держать tight coupling по импорту
    приватной функции synthesize не хочется.
    """
    goal = anchor.goal
    if goal is None:
        bmi = anchor.weight_kg / ((anchor.height_cm / 100.0) ** 2)
        if anchor.body_fat_percent > 25 or bmi > 27:
            goal = "weight_loss"
        elif anchor.body_fat_percent < 18 and bmi < 24:
            goal = "muscle_gain"
        else:
            goal = "maintenance"

    level = anchor.training_level or "intermediate"

    return UserContext(
        goal=goal,
        level=level,
        sex=anchor.sex,
        age=anchor.age_years,
        height_cm=anchor.height_cm,
        weight_kg=anchor.weight_kg,
        body_fat_percent=anchor.body_fat_percent,
        equipment_available=equipment_available,
    )


def _sample_user_equipment(rng: random.Random) -> tuple[str, ...]:
    """Случайный профиль оборудования. Распределение примерное:
    65% «полный зал», 25% «домашний» (только bodyweight + dumbbell),
    10% «street workout» (bodyweight + pullup_bar).

    Это синтетика — в S3/S4 явного поля equipment нет; но без вариативности
    модель получит постоянное `equipment_available`-фичу и не научится
    на ней. Поэтому варьируем.
    """
    r = rng.random()
    if r < 0.65:
        return (
            "barbell",
            "dumbbell",
            "machine",
            "cable",
            "bench",
            "pullup_bar",
            "kettlebell",
            "resistance_band",
            "medicine_ball",
            "other",
        )
    if r < 0.90:
        return ("dumbbell", "resistance_band", "kettlebell")
    return ("pullup_bar",)


def build_rows(
    anchors: list[Anchor],
    *,
    catalog: list[_CatalogExercise],
    salt: str,
    seed: int = DEFAULT_SEED,
    per_user_exercises: int = DEFAULT_PER_USER_EXERCISES,
) -> Iterable[tuple[dict[str, Any], str]]:
    """`(row, split)` итерация. Pure функция — без I/O, для unit-тестов.

    Делает: импутация anchors → семпл equipment → семпл подмножества
    каталога → relevance label. На каждого user'а возвращает
    `per_user_exercises` строк (или меньше, если каталог короче).
    """
    cleaned, _stats = filter_and_impute(anchors)
    # Сплит идёт по anon_user_id, чтобы один и тот же raw_user_id
    # после анонимизации не оказался в двух сплитах разом.
    anon_ids_by_raw = {
        a.raw_user_id: anon_user_id(a.raw_user_id, salt=salt) for a in cleaned
    }
    splits = split_users(anon_ids_by_raw.values(), seed=seed)
    rng = random.Random(seed)
    catalog_size = len(catalog)
    indices = list(range(catalog_size))

    for anchor in cleaned:
        anon_id = anon_ids_by_raw[anchor.raw_user_id]
        equipment = _sample_user_equipment(rng)
        user_ctx = _anchor_to_user_context(
            anchor, equipment_available=equipment
        )
        # Случайная выборка упражнений: не все 873, чтобы датасет был
        # управляемым; rng зафиксирован — детерминированно при том же seed.
        rng.shuffle(indices)
        sample_size = min(per_user_exercises, catalog_size)
        for idx in indices[:sample_size]:
            ex = catalog[idx]
            ex_ctx = ex.to_context()
            r: RelevanceScore = relevance(user_ctx, ex_ctx)
            row = {
                "anon_user_id": anon_id,
                "user_age": anchor.age_years,
                "user_sex_male": 1 if anchor.sex == "male" else 0,
                "user_height_cm": anchor.height_cm,
                "user_weight_kg": anchor.weight_kg,
                "user_body_fat": anchor.body_fat_percent,
                "user_goal": user_ctx.goal,
                "user_level": user_ctx.level,
                "user_equipment_count": len(equipment),
                "exercise_id": ex.exercise_id,
                "primary_muscle_group": ex.primary_muscle_group,
                "body_region": ex.body_region,
                "is_advanced": int(ex_ctx.is_advanced),
                "needs_barbell": int("barbell" in ex.equipment),
                "needs_dumbbell": int("dumbbell" in ex.equipment),
                "needs_machine": int("machine" in ex.equipment),
                "needs_bodyweight_only": int(
                    set(ex.equipment) <= {"bodyweight"}
                ),
                "score": r.score,
                "label": r.label,
                "excluded_by_equipment": int(r.excluded_by_equipment),
            }
            yield row, splits[anon_id]


_CSV_FIELDS: tuple[str, ...] = (
    "anon_user_id",
    "user_age",
    "user_sex_male",
    "user_height_cm",
    "user_weight_kg",
    "user_body_fat",
    "user_goal",
    "user_level",
    "user_equipment_count",
    "exercise_id",
    "primary_muscle_group",
    "body_region",
    "is_advanced",
    "needs_barbell",
    "needs_dumbbell",
    "needs_machine",
    "needs_bodyweight_only",
    "score",
    "label",
    "excluded_by_equipment",
    "split",
)


def run(
    *,
    anchors: list[Anchor],
    catalog_path: Path,
    out_dir: Path,
    seed: int = DEFAULT_SEED,
    salt: str = "fitness-tracker-thesis",
    per_user_exercises: int = DEFAULT_PER_USER_EXERCISES,
) -> dict[str, Any]:
    """Записать CSV + meta. Возвращает stats для CLI/тестов."""
    catalog = load_catalog(catalog_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "dataset_c_workout_recommender.csv"
    n = 0
    pos = 0
    excluded = 0
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for row, split in build_rows(
            anchors,
            catalog=catalog,
            salt=salt,
            seed=seed,
            per_user_exercises=per_user_exercises,
        ):
            n += 1
            pos += row["label"]
            excluded += row["excluded_by_equipment"]
            row["split"] = split
            writer.writerow(row)

    meta = {
        "version": DATASET_VERSION,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "rows": n,
        "positives": pos,
        "positive_ratio": round(pos / n, 4) if n else 0.0,
        "excluded_by_equipment": excluded,
        "seed": seed,
        "per_user_exercises": per_user_exercises,
        "catalog_size": len(catalog),
    }
    (out_dir / "dataset_c_workout_recommender.meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return meta
