"""Чистая логика генератора тренировок — spec 006.

Слой `domain/workout_generator/` — никакого I/O и БД, только трансформации
над Python-структурами. Здесь:

- `composer.py` — детерминированный композитор: получив upper/lower/core
  ranking от ML и rule-based ограничения (frequency, balance, прогрессия),
  собирает 4-недельный план;
- `progression.py` — Linear/Double Progression: вес/повторения/подходы
  по неделям 1..4 в зависимости от уровня подготовки;
- `templates.py` — fallback'и (REQ-16): встроенные шаблоны планов на
  случай, если ML-recommender недоступен (3-day full body, 4-day
  upper/lower, 5-day push/pull/legs/upper/lower).

ML-обвязка (lazy-load lgbm-артефакта) лежит в `domains/workout_generator/`
рядом с БД-сервисом. Это аналогично разделению `forecast` — pure
helper'ы отдельно от БД/ML-инференса.
"""

from .composer import (
    PlanComposed,
    PlanDayComposed,
    PlanExerciseComposed,
    compose_plan,
)
from .progression import progress_week
from .templates import FallbackTemplate, fallback_plan, pick_template

__all__ = [
    "FallbackTemplate",
    "PlanComposed",
    "PlanDayComposed",
    "PlanExerciseComposed",
    "compose_plan",
    "fallback_plan",
    "pick_template",
    "progress_week",
]
