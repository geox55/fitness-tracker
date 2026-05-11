"""Pure helpers для прогресса по упражнению — spec 010 REQ-09.

Сервис тянет из БД сырые строки (date, weight, reps) одного упражнения
в окне и передаёт сюда. Здесь — только две вещи:

- `epley_1rm` — оценка 1-rep max по формуле Эпли: w * (1 + r/30).
  Достаточно точна для рабочих весов 1..12 повторений; для очень
  больших r вне зала её не используют, и spec этого не требует.
- `build_exercise_progress` — группировка по ISO-неделям с агрегатами:
  best_weight_kg, best_e1rm_kg, sets, tonnage_kg. Возвращает список,
  отсортированный по `week_start` (понедельник недели лога).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta


def epley_1rm(*, weight_kg: float, reps: int) -> float:
    """Оценка 1RM по Эпли: `w * (1 + reps/30)`.

    Защищаем от отрицательного веса и нуля повторений — таких логов в
    `ExerciseLog` быть не должно (CHECK constraint reps ≥ 1, weight ≥ 0),
    но helper переиспользуется и за пределами БД-обвязки, так что
    валидация here-and-now дешевле, чем NaN-ы в графике.
    """
    if reps < 1:
        raise ValueError("reps must be ≥ 1")
    if weight_kg < 0:
        raise ValueError("weight_kg must be ≥ 0")
    return weight_kg * (1.0 + reps / 30.0)


def _iso_week_start(d: date) -> date:
    """Понедельник недели, в которой лежит `d` (date.weekday(): Mon=0)."""
    return d - timedelta(days=d.weekday())


@dataclass(frozen=True)
class ExerciseProgressWeek:
    """Один интервал серии — неделя с агрегатами по упражнению.

    Поля:
    - `best_weight_kg` — лучший рабочий вес в неделю (на любой реп);
    - `best_e1rm_kg` — лучший оценочный 1RM за неделю (по Эпли);
    - `sets` — количество non-skipped сетов;
    - `tonnage_kg` — Σ(reps × weight) за неделю.
    """

    week_start: date
    best_weight_kg: float
    best_e1rm_kg: float
    sets: int
    tonnage_kg: float


def build_exercise_progress(
    *,
    rows: Iterable[tuple[date, float, int]],
) -> list[ExerciseProgressWeek]:
    """Свернуть (date, weight, reps)-строки в по-недельные агрегаты.

    Если `rows` пуст — пустой список (UI рисует empty state).
    """
    buckets: dict[date, list[tuple[float, int]]] = {}
    for d, weight, reps in rows:
        buckets.setdefault(_iso_week_start(d), []).append((weight, reps))

    out: list[ExerciseProgressWeek] = []
    for week_start in sorted(buckets):
        logs = buckets[week_start]
        best_weight = max(w for w, _ in logs)
        best_e1rm = max(epley_1rm(weight_kg=w, reps=r) for w, r in logs)
        tonnage = sum(w * r for w, r in logs)
        out.append(
            ExerciseProgressWeek(
                week_start=week_start,
                best_weight_kg=best_weight,
                best_e1rm_kg=round(best_e1rm, 2),
                sets=len(logs),
                tonnage_kg=round(tonnage, 2),
            )
        )
    return out


__all__ = [
    "ExerciseProgressWeek",
    "build_exercise_progress",
    "epley_1rm",
]
