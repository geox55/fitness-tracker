"""Чистая логика генератора тренировок — spec 006.

Слой `domain/workout_generator/` — pure functions, никакого I/O и БД.

- `progression.py` — Linear/Double прогрессия по неделям 1..4 (REQ-09).
- `templates.py`   — сплиты, схемы подходов, кардио-блоки (REQ-04/05/08/10).
- `composer.py`    — rule-based fallback (REQ-16) + валидатор плана.

ML-ранкер (когда он подъедет в API) сможет переопределить порядок выбора
в `_pick_for_slot`, но composer останется идентичным в части прогрессии
и сборки — это для воспроизводимости (NFR-02).
"""

from .composer import (
    COMPOSER_VERSION,
    ExercisePool,
    PlannedDay,
    PlannedExercise,
    PlannedPlan,
    PlannedWeek,
    UserContext,
    compose_plan,
)
from .progression import SetTarget, progress_week
from .recommender import (
    MlRanker,
    RankerExerciseFeatures,
    RankerUserFeatures,
    load_ranker,
    score_exercises,
)
from .templates import SetScheme, base_scheme, is_compound, strength_split

__all__ = [
    "COMPOSER_VERSION",
    "ExercisePool",
    "MlRanker",
    "PlannedDay",
    "PlannedExercise",
    "PlannedPlan",
    "PlannedWeek",
    "RankerExerciseFeatures",
    "RankerUserFeatures",
    "SetScheme",
    "SetTarget",
    "UserContext",
    "base_scheme",
    "compose_plan",
    "is_compound",
    "load_ranker",
    "progress_week",
    "score_exercises",
    "strength_split",
]
