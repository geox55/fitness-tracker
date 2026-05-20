from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ...domain.analytics import COMPARABLE_FIELDS, SERIES_METRICS  # noqa: F401


class OverviewMetrics(BaseModel):
    workouts_this_month: int
    total_weight_kg: int
    total_weight_delta_percent: int
    active_streak_days: int
    streak_is_personal_best: bool


class StrengthPoint(BaseModel):
    day_offset: int  # дни от начала окна (0..30)
    weight_kg: float


class StrengthProgress(BaseModel):
    exercise_title: str | None
    current_max_kg: int
    points: list[StrengthPoint]


class RecentWorkoutItem(BaseModel):
    id: UUID
    performed_at: datetime
    day_label: str
    title: str
    sets: int
    reps: int
    weight_kg: int
    kind: str  # full_body | push | legs | pull | cardio | other


class OverviewResponse(BaseModel):
    month: date  # первый день месяца
    metrics: OverviewMetrics
    strength: StrengthProgress | None
    recent: list[RecentWorkoutItem]


# ---------------------------------------------------------------------------
# Spec 010 §9 — серии InBody и сравнение замеров
# ---------------------------------------------------------------------------


class SeriesPoint(BaseModel):
    """Точка истории по выбранной метрике."""

    date: date
    value: float


class ForecastSeriesPoint(BaseModel):
    """Точка прогноза с CI-полосой; date вычислен по horizon_weeks (REQ-03)."""

    date: date
    value: float
    ci_low: float
    ci_high: float


class ForecastSeries(BaseModel):
    points: list[ForecastSeriesPoint]


class InBodySeriesResponse(BaseModel):
    """Ответ /analytics/inbody.

    `forecast` — None, если метрика не в spec 008 FORECASTABLE_METRICS
    (например, bmi, protein_kg). UI скроет пунктир.
    """

    metric: str
    points: list[SeriesPoint]
    forecast: ForecastSeries | None


class FieldDeltaSchema(BaseModel):
    """Дельта одной метрики между двумя замерами (compare-таблица)."""

    field: str
    value_a: float | None
    value_b: float | None
    delta_absolute: float | None
    delta_percent: float | None


class CompareMeasurement(BaseModel):
    """Шапка compare-ответа: id + дата, без полного измерения, чтобы не
    тащить storage/signed URL в эндпоинт сравнения.
    """

    id: UUID
    measured_at: datetime


class CompareResponse(BaseModel):
    a: CompareMeasurement
    b: CompareMeasurement
    deltas: list[FieldDeltaSchema]


# ---------------------------------------------------------------------------
# Spec 010 §3 Scenario 4 — серия по тренировкам (тоннаж + количество)
# ---------------------------------------------------------------------------


class WorkoutsBucket(BaseModel):
    """Один интервал серии (день/неделя/месяц) с агрегатами тренировок."""

    period_start: date
    tonnage_kg: float
    workouts_count: int


class WorkoutsAnalyticsResponse(BaseModel):
    """Эхо bucket + список бакетов в порядке возрастания period_start."""

    bucket: str
    items: list[WorkoutsBucket]


# ---------------------------------------------------------------------------
# Spec 010 §3 Scenario 3 — прогресс по цели (REQ-05/06)
# ---------------------------------------------------------------------------


class GoalProgressResponse(BaseModel):
    """Положительный ответ /analytics/goal-progress.

    `eta` — None, если прогноз не построился или цель за горизонтом.
    `already_reached` — True если current уже на/за target (тогда
    `progress_percent` = 100). UI в этом случае может предлагать
    «обновить цель».
    """

    goal: str  # "weight_loss" | "muscle_gain"
    start_value: float
    current_value: float
    target_value: float
    progress_percent: int
    already_reached: bool
    started_at: date
    eta: date | None
    eta_confidence: str | None  # "low" | "medium" | "high"


class ExerciseProgressWeekItem(BaseModel):
    """Один интервал серии по упражнению — неделя (понедельник)."""

    week_start: date
    best_weight_kg: float
    best_e1rm_kg: float
    sets: int
    tonnage_kg: float


class ExerciseProgressResponse(BaseModel):
    """Ответ /analytics/exercise-progress (REQ-09).

    `exercise_title` — русское имя из каталога с фоллбеком на латинское;
    `weeks` — массив, отсортированный по `week_start` (может быть пустым).
    """

    exercise_id: UUID
    exercise_title: str | None
    weeks: list[ExerciseProgressWeekItem]


class TrainedExerciseItem(BaseModel):
    """Упражнение, по которому у пользователя есть хотя бы один non-skipped
    лог в завершённой тренировке. Используется как стартовый список на
    экране «Прогресс по упражнению» — чтобы не заставлять искать вручную."""

    id: UUID
    exercise_name: str
    exercise_name_ru: str | None
    primary_muscle_group: str
    equipment: list[str]
    sets_count: int
    last_logged_at: date


class TrainedExercisesResponse(BaseModel):
    items: list[TrainedExerciseItem]


class GoalProgressEmptyResponse(BaseModel):
    """Empty-state: профиль не готов к показу прогресс-бара. UI рисует CTA.

    `reason` — машинный код (`no_goal_in_profile` | `no_target_set` |
    `no_inbody_measurements`); `missing_fields` — что именно надо
    заполнить, чтобы раздел заработал.
    """

    reason: str
    missing_fields: list[str]


# ---------------------------------------------------------------------------
# Spec 010 §3 Scenario 5 — экспорт PDF-отчёта (REQ-10..12)
# ---------------------------------------------------------------------------


class ExportPdfRequest(BaseModel):
    """Параметры запроса POST /analytics/export-pdf.

    Все поля опциональны: `period_from`/`period_to=None` → «вся история»,
    `sections=None` → все секции (profile/inbody/workouts/goal). Это нужно
    UI, чтобы можно было показать «быстрый» экспорт без выбора.
    """

    period_from: date | None = Field(default=None, alias="from")
    period_to: date | None = Field(default=None, alias="to")
    sections: list[str] | None = None

    model_config = {"populate_by_name": True}


class ExportPdfJobAcceptedResponse(BaseModel):
    """Ответ 202 на старте: клиент получает job_id и опрашивает status."""

    job_id: UUID
    status: str  # pending | running | ready | failed


class ExportPdfJobStatusResponse(BaseModel):
    """Полный статус job'а.

    `url`/`expires_at` заполняются только в `status == 'ready'`. В failed
    смотрим `error_message`. В pending/running клиент должен опросить
    ещё раз через ~1 сек.
    """

    job_id: UUID
    status: str
    url: str | None = None
    expires_at: datetime | None = None
    error_message: str | None = None
    sections: list[str]
    period_from: date | None
    period_to: date | None
    created_at: datetime
    ready_at: datetime | None
