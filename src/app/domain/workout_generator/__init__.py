"""Чистая логика генератора тренировок — spec 006 (WIP).

Слой `domain/workout_generator/` — никакого I/O и БД. На текущей итерации
готов только `progression.py` (Linear/Double Progression по неделям 1..4).
Composer + fallback templates — следующим заходом, см. дипломную главу
Егора (`docs/thesis/workout_recommender_metrics.md`, §6).
"""

from .progression import SetTarget, progress_week

__all__ = ["SetTarget", "progress_week"]
