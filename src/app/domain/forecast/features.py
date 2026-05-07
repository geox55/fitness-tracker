"""Сборка фичей для предиктора InBody.

Входные данные приходят из БД (см. service.py), но сама сборка — чистая
функция: на вход примитивы (списки кортежей), на выход — `FeatureSnapshot`.
Это нужно, чтобы тестировать predictor целиком без интеграции с Postgres.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

Goal = Literal["weight_loss", "muscle_gain", "maintenance"]
Sex = Literal["male", "female"]


@dataclass(frozen=True)
class InBodyPoint:
    """Минимальный slate InBody-измерения для предиктора."""

    measured_at: datetime
    weight_kg: float
    body_fat_percent: float
    muscle_mass_kg: float | None


@dataclass(frozen=True)
class TrainingAggregate:
    """Агрегаты тренировок за неделю — то, на что смотрит модель.

    `tonnage_kg` = Σ(reps · weight) по всем подходам в окне;
    `count` — число завершённых тренировок;
    `avg_duration_min` — средняя длительность.
    """

    week_start: datetime
    tonnage_kg: float
    count: int
    avg_duration_min: float


@dataclass(frozen=True)
class FeatureSnapshot:
    """Полный набор фичей на момент прогноза.

    `goal_changed_within_days` — для эджа из §10: смена цели обнуляет confidence
    до medium на 4 недели. None означает «никогда не менялась» / «нет данных».
    """

    inbody_history: tuple[InBodyPoint, ...]
    training_weeks: tuple[TrainingAggregate, ...]
    target_calories_kcal: int | None
    actual_calories_kcal: int | None
    goal: Goal | None
    training_frequency: int | None
    sex: Sex | None
    age_years: int | None
    height_cm: float | None
    goal_changed_within_days: int | None
    now: datetime

    @property
    def latest(self) -> InBodyPoint | None:
        """Последний InBody — None, если истории нет (Edge case + cold-start)."""
        return self.inbody_history[-1] if self.inbody_history else None

    @property
    def history_span_days(self) -> int:
        if len(self.inbody_history) < 2:
            return 0
        return (
            self.inbody_history[-1].measured_at - self.inbody_history[0].measured_at
        ).days

    @property
    def last_inbody_age_days(self) -> int | None:
        if self.latest is None:
            return None
        return (self.now - self.latest.measured_at).days

    @property
    def trainings_last_8w(self) -> int:
        cutoff = self.now - timedelta(weeks=8)
        return sum(t.count for t in self.training_weeks if t.week_start >= cutoff)


def _to_float(v: float | None) -> float | None:
    return float(v) if v is not None else None


def build_feature_snapshot(
    *,
    inbody_history: list[InBodyPoint],
    training_weeks: list[TrainingAggregate] | None = None,
    target_calories_kcal: int | None = None,
    actual_calories_kcal: int | None = None,
    goal: Goal | None = None,
    training_frequency: int | None = None,
    sex: Sex | None = None,
    age_years: int | None = None,
    height_cm: float | None = None,
    goal_changed_within_days: int | None = None,
    now: datetime,
) -> FeatureSnapshot:
    """Собрать снапшот, отсортировав историю по measured_at ASC."""
    sorted_history = tuple(sorted(inbody_history, key=lambda p: p.measured_at))
    return FeatureSnapshot(
        inbody_history=sorted_history,
        training_weeks=tuple(training_weeks or ()),
        target_calories_kcal=target_calories_kcal,
        actual_calories_kcal=actual_calories_kcal,
        goal=goal,
        training_frequency=training_frequency,
        sex=sex,
        age_years=age_years,
        height_cm=_to_float(height_cm) if height_cm is not None else None,
        goal_changed_within_days=goal_changed_within_days,
        now=now,
    )


# Используется service.py для записи в `input_features` (NFR-04).
def serialize_features(snap: FeatureSnapshot) -> dict[str, object]:
    return {
        "n_inbody": len(snap.inbody_history),
        "history_span_days": snap.history_span_days,
        "last_inbody_age_days": snap.last_inbody_age_days,
        "trainings_last_8w": snap.trainings_last_8w,
        "target_calories_kcal": snap.target_calories_kcal,
        "actual_calories_kcal": snap.actual_calories_kcal,
        "goal": snap.goal,
        "training_frequency": snap.training_frequency,
        "sex": snap.sex,
        "age_years": snap.age_years,
        "goal_changed_within_days": snap.goal_changed_within_days,
    }
