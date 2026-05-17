"""БД-обвязка для планов — spec 006.

Что здесь живёт:
- `generate_plan` — собирает фичи пользователя, дёргает rule-based
  composer, сохраняет план в БД (с архивированием предыдущего active);
- `get_active`, `get_by_id`, `archive`, `list_for_user` — CRUD.

Чистая логика композиции живёт в `app.domain.workout_generator.composer`.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.workout_generator import (
    COMPOSER_VERSION,
    ExercisePool,
    RankerExerciseFeatures,
    RankerUserFeatures,
    UserContext,
    compose_plan,
    load_ranker,
    score_exercises,
)
from ..catalog.models import Exercise
from ..inbody.models import InBodyMeasurement
from ..profile.models import UserProfile
from .models import PlanDay, PlanExercise, PlanWeek, WorkoutPlan

_log = logging.getLogger(__name__)

# Дефолтный пул оборудования. Используется, если ни override.equipment_available,
# ни profile.equipment_available не заданы (spec 004 REQ-09: NULL в профиле =
# «не настраивал»). «Коммерческий зал»: типовой набор, под который calibrated
# rule-based composer.
DEFAULT_EQUIPMENT_AVAILABLE: tuple[str, ...] = (
    "barbell",
    "dumbbell",
    "bench",
    "pullup_bar",
    "bodyweight",
    "machine",
    "cable",
)


class PlanError(Exception):
    code: str = "plan_error"


class PreconditionsNotMet(PlanError):
    """Профиль не заполнен или нет InBody — REQ-01 spec 006."""

    code = "preconditions_not_met"

    def __init__(self, missing: list[str]) -> None:
        super().__init__(f"missing fields: {missing}")
        self.missing = missing

    def as_http_detail(self, message: str) -> dict[str, object]:
        """Формат для `HTTPException.detail` — используется и в
        `/plans/generate`, и в `/plans/rebuild`, чтобы PWA-клиент видел
        один и тот же контракт ошибки."""
        return {
            "error": self.code,
            "missing": self.missing,
            "message": message,
        }


class PlanNotFoundError(PlanError):
    code = "plan_not_found"


class ActivePlanRaceError(PlanError):
    """Параллельный генератор успел создать active-план первым.

    Partial unique index `uq_workout_plans_one_active` ловит гонку
    на уровне БД; мы маппим её в осмысленную 409, чтобы клиент не
    видел 500 при двойном клике.
    """

    code = "active_plan_already_exists"


# ---------------------------------------------------------------------------
# Feature gathering
# ---------------------------------------------------------------------------


def _check_preconditions(
    profile: UserProfile | None,
    *,
    goal_override: str | None,
    level_override: str | None,
    frequency_override: int | None,
) -> None:
    """Профиль завершён? Есть всё необходимое для модели?

    Override может закрыть пропуск конкретного поля (что-если scenario), но
    если override тоже None — поле обязано быть в профиле.
    """
    missing: list[str] = []
    if profile is None:
        # Все поля идут как пропущенные.
        missing.extend(["goal", "training_level", "training_frequency"])
    else:
        if goal_override is None and profile.goal is None:
            missing.append("goal")
        if level_override is None and profile.training_level is None:
            missing.append("training_level")
        if frequency_override is None and profile.training_frequency is None:
            missing.append("training_frequency")
    if missing:
        raise PreconditionsNotMet(missing=missing)


async def _gather_inbody_features(
    session: AsyncSession, *, user_id: uuid.UUID
) -> tuple[InBodyMeasurement | None, list[str]]:
    """Последний InBody-замер + список пропущенных полей для warning.

    REQ-02: модель учитывает вес/жир/мышцы/BMR из последнего snapshot.
    Если замеров нет — возвращаем (None, ["inbody"]) и пишем warning;
    REQ-01 формально требует ≥1 замер, но spec 006 §10 «Нет InBody → AI
    использует baseline из профиля + дисклеймер».
    """
    stmt = (
        select(InBodyMeasurement)
        .where(InBodyMeasurement.user_id == user_id)
        .order_by(desc(InBodyMeasurement.measured_at))
        .limit(1)
    )
    last = (await session.execute(stmt)).scalar_one_or_none()
    return last, ([] if last is not None else ["inbody"])


async def _gather_pool(
    session: AsyncSession, *, equipment_available: tuple[str, ...]
) -> list[ExercisePool]:
    """Все упражнения каталога — фильтрация по equipment живёт в композере,
    т.к. equipment-чек для разных слотов одинаковый и не зависит от выбора.

    Грузим всё одной выборкой. Каталог ~500 упражнений (spec 004 REQ-01) —
    держим в памяти.
    """
    stmt = select(Exercise)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        ExercisePool(
            id=str(ex.id),
            name=ex.exercise_name,
            name_ru=ex.exercise_name_ru,
            primary_muscle_group=ex.primary_muscle_group,
            secondary_muscle_groups=tuple(ex.secondary_muscle_group or ()),
            equipment=tuple(ex.equipment or ()),
            body_region=ex.body_region,
        )
        for ex in rows
    ]


# ---------------------------------------------------------------------------
# ML ranker: lazy load + scoring пула. На любой ошибке возвращаем None —
# composer тогда падает на rule-based scoring (spec 006 §2 / REQ-16).
# ---------------------------------------------------------------------------


def _age_years_from_birth(birth_date: date | None, *, now: datetime) -> int | None:
    """Полных лет на now. None если birth_date неизвестен — ML тогда не
    запустим (фича `user_age` обязательна в train-сигнатуре)."""
    if birth_date is None:
        return None
    today = now.date()
    years = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return max(0, years)


def _build_ranker_user_features(
    *,
    profile: UserProfile,
    last_inbody: InBodyMeasurement | None,
    equipment_available: tuple[str, ...],
    goal: str,
    level: str,
    now: datetime,
) -> RankerUserFeatures | None:
    """Собрать user-часть фичей. None означает «фичей не хватает» —
    тогда не запускаем ML, идём на rule-based.

    Источники:
    - `age` — из birth_date профиля;
    - `sex_male`, `height_cm` — из профиля;
    - `weight_kg`, `body_fat_percent` — приоритет последнему InBody, иначе
      profile.baseline_weight_kg / дефолт 20.0 для жира (типичная медиана
      Dataset-C). Дефолт намеренно: иначе при пустом InBody ML не запустится
      даже для пользователей с полным профилем.
    """
    age = _age_years_from_birth(profile.birth_date, now=now)
    if age is None or profile.sex is None or profile.height_cm is None:
        return None

    if last_inbody is not None:
        weight = float(last_inbody.weight_kg)
        body_fat = (
            float(last_inbody.body_fat_percent)
            if last_inbody.body_fat_percent is not None
            else 20.0
        )
    elif profile.baseline_weight_kg is not None:
        weight = float(profile.baseline_weight_kg)
        body_fat = 20.0
    else:
        return None

    return RankerUserFeatures(
        age=age,
        sex_male=1 if profile.sex == "male" else 0,
        height_cm=float(profile.height_cm),
        weight_kg=weight,
        body_fat_percent=body_fat,
        equipment_count=len(equipment_available),
        goal=goal,
        level=level,
    )


def _try_score_pool(
    pool: list[ExercisePool],
    *,
    profile: UserProfile,
    last_inbody: InBodyMeasurement | None,
    equipment_available: tuple[str, ...],
    goal: str,
    level: str,
    now: datetime,
) -> tuple[dict[str, float] | None, str | None]:
    """Попробовать получить ML-скоры для всего пула.

    Возвращает `(scores, model_version)`; при любой ошибке/недоступности —
    `(None, None)`, и сервис идёт по rule-based ветке. Логируем причину,
    чтобы не съесть проблему молча (как делает forecast/service.py).
    """
    ranker = load_ranker()
    if ranker is None:
        return None, None

    user_features = _build_ranker_user_features(
        profile=profile,
        last_inbody=last_inbody,
        equipment_available=equipment_available,
        goal=goal,
        level=level,
        now=now,
    )
    if user_features is None:
        return None, None

    exercise_features = [
        RankerExerciseFeatures(
            exercise_id=ex.id,
            primary_muscle_group=ex.primary_muscle_group,
            body_region=ex.body_region,
            equipment=ex.equipment,
            name=ex.name,
        )
        for ex in pool
    ]
    try:
        scores = score_exercises(
            ranker, user=user_features, exercises=exercise_features
        )
    except Exception:
        # ML-инференс не должен валить генерацию — fallback к rule-based,
        # причину пишем в лог (та же стратегия, что у forecast/service.py).
        _log.exception("ML ranker inference failed, falling back to rule-based")
        return None, None
    return scores, ranker.model_version


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------


async def generate_plan(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    override_goal: str | None = None,
    override_level: str | None = None,
    override_frequency: int | None = None,
    override_equipment: list[str] | None = None,
    now: datetime | None = None,
) -> tuple[WorkoutPlan, list[str]]:
    """Сгенерировать новый план; вернуть его + warnings композера.

    Поток:
    1. Достаём профиль; проверяем preconditions (REQ-01).
    2. Собираем фичи (последний InBody, каталог).
    3. Через `compose_plan` получаем `PlannedPlan`.
    4. Архивируем текущий active (REQ-13).
    5. Persist'им новый план как active. Возвращаем ORM + warnings.

    `now` инжектится в тестах для воспроизводимости (NFR-02).
    """
    now = now or datetime.now(UTC)

    profile = (
        await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
    ).scalar_one_or_none()
    _check_preconditions(
        profile,
        goal_override=override_goal,
        level_override=override_level,
        frequency_override=override_frequency,
    )
    assert profile is not None  # для mypy — preconditions проверены

    goal = override_goal or profile.goal
    level = override_level or profile.training_level
    frequency = override_frequency or profile.training_frequency
    # Приоритет: явный override > профиль (spec 004 REQ-09) > DEFAULT.
    # profile.equipment_available может быть `[]` — это «явно ничего»,
    # т.е. валидный пустой набор; не путаем с None («не настраивал»).
    if override_equipment is not None:
        equipment = tuple(override_equipment)
    elif profile.equipment_available is not None:
        equipment = tuple(profile.equipment_available)
    else:
        equipment = DEFAULT_EQUIPMENT_AVAILABLE

    # Снапшот фичей для воспроизводимости (REQ-15).
    bodyweight_kg = (
        float(profile.baseline_weight_kg)
        if profile.baseline_weight_kg is not None
        else None
    )
    last_inbody, warn_missing = await _gather_inbody_features(
        session, user_id=user_id
    )
    if last_inbody is not None:
        bodyweight_kg = float(last_inbody.weight_kg)

    pool = await _gather_pool(session, equipment_available=equipment)

    user_ctx = UserContext(
        goal=goal,  # type: ignore[arg-type]
        level=level,  # type: ignore[arg-type]
        frequency=frequency,  # type: ignore[arg-type]
        equipment_available=equipment,
        bodyweight_kg=bodyweight_kg,
    )

    # Spec 006 §2: гибрид — ML ранкер + rule-based composer. При отсутствии
    # артефакта/joblib (`(None, None)`) composer работает один — REQ-16.
    ml_scores, ranker_version = _try_score_pool(
        pool,
        profile=profile,
        last_inbody=last_inbody,
        equipment_available=equipment,
        goal=goal,  # type: ignore[arg-type]  # preconditions гарантируют не-None
        level=level,  # type: ignore[arg-type]
        now=now,
    )
    plan_model_version = (
        f"hybrid-{COMPOSER_VERSION}+{ranker_version}"
        if ranker_version is not None
        else COMPOSER_VERSION
    )

    composed = compose_plan(
        user=user_ctx,
        pool=pool,
        ml_scores=ml_scores,
        model_version=plan_model_version,
    )
    all_warnings: list[str] = list(composed.warnings)
    if "inbody" in warn_missing:
        all_warnings.insert(
            0,
            "Замеров InBody нет: план собран на основе baseline_weight_kg из профиля. "
            "Добавьте измерение для точности.",
        )

    # Архивируем активный план, если есть (REQ-13: только один active).
    prev_active = (
        await session.execute(
            select(WorkoutPlan).where(
                WorkoutPlan.user_id == user_id,
                WorkoutPlan.status == "active",
            )
        )
    ).scalar_one_or_none()
    if prev_active is not None:
        prev_active.status = "archived"
        prev_active.archived_at = now
        await session.flush()

    plan = WorkoutPlan(
        user_id=user_id,
        status="active",
        generated_at=now,
        valid_until=(now + timedelta(weeks=4)).date(),
        goal=goal,
        training_level=level,
        frequency=frequency,
        input_features=_build_features_snapshot(
            profile=profile,
            last_inbody=last_inbody,
            user_ctx=user_ctx,
        ),
        model_version=composed.model_version,
    )
    session.add(plan)
    try:
        await session.flush()  # нужен plan.id для FK
    except IntegrityError as exc:
        # Гонка двух параллельных generate_plan: partial unique index
        # `uq_workout_plans_one_active` пропустил только одного. Откатываем
        # текущий savepoint, чтобы сессия не «зависала», и поднимаем
        # доменную ошибку — HTTP-слой замапит её в 409.
        await session.rollback()
        raise ActivePlanRaceError("active plan already exists") from exc

    for week_payload in composed.weeks:
        week = PlanWeek(plan_id=plan.id, week_no=week_payload.week_no)
        session.add(week)
        await session.flush()
        for day_payload in week_payload.days:
            day = PlanDay(
                week_id=week.id,
                day_no=day_payload.day_no,
                name=day_payload.name,
                type=day_payload.type,
            )
            session.add(day)
            await session.flush()
            for ex_payload in day_payload.exercises:
                # Cardio-дни идут без каталожного exercise — exercise_id
                # хранится NULL в БД (поле тогда становится notes-only).
                exercise_uuid: uuid.UUID | None = (
                    uuid.UUID(ex_payload.exercise_id)
                    if ex_payload.exercise_id
                    else None
                )
                if exercise_uuid is None:
                    # Используем «placeholder»: первый exercise из пула
                    # как FK-ссылка не подойдёт. Cardio храним как
                    # отдельную модель в фазе 2; пока — пропускаем БД-запись
                    # и кладём только в notes (план откроется без cardio).
                    continue
                session.add(
                    PlanExercise(
                        day_id=day.id,
                        order_no=ex_payload.order_no,
                        exercise_id=exercise_uuid,
                        target_sets=ex_payload.target_sets,
                        target_reps_min=ex_payload.target_reps_min,
                        target_reps_max=ex_payload.target_reps_max,
                        target_rpe=ex_payload.target_rpe,
                        rest_seconds=ex_payload.rest_seconds,
                        target_weight_kg=(
                            Decimal(str(ex_payload.target_weight_kg))
                            if ex_payload.target_weight_kg is not None
                            else None
                        ),
                        notes=ex_payload.notes,
                    )
                )

    # При смене цели в spec 002 поднимается plan_rebuild_required —
    # после генерации сбрасываем флаг.
    if profile.plan_rebuild_required:
        profile.plan_rebuild_required = False

    await session.flush()
    return plan, all_warnings


def _build_features_snapshot(
    *,
    profile: UserProfile,
    last_inbody: InBodyMeasurement | None,
    user_ctx: UserContext,
) -> dict[str, Any]:
    """REQ-15: что подавалось в композер; PII не пишем (NFR-04)."""
    return {
        "user_context": {
            "goal": user_ctx.goal,
            "level": user_ctx.level,
            "frequency": user_ctx.frequency,
            "equipment_available": list(user_ctx.equipment_available),
            "bodyweight_kg": user_ctx.bodyweight_kg,
        },
        "profile_snapshot": {
            "goal": profile.goal,
            "training_level": profile.training_level,
            "training_frequency": profile.training_frequency,
            "baseline_weight_kg": (
                float(profile.baseline_weight_kg)
                if profile.baseline_weight_kg is not None
                else None
            ),
            "bmr_kcal": profile.bmr_kcal,
        },
        "inbody_snapshot": (
            {
                "measured_at": last_inbody.measured_at.isoformat(),
                "weight_kg": float(last_inbody.weight_kg),
                "body_fat_percent": float(last_inbody.body_fat_percent),
                "muscle_mass_kg": (
                    float(last_inbody.muscle_mass_kg)
                    if last_inbody.muscle_mass_kg is not None
                    else None
                ),
                "bmr_kcal": last_inbody.bmr_kcal,
            }
            if last_inbody is not None
            else None
        ),
    }


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------


def _select_with_relations() -> Any:
    """Eager-load иерархии плана: weeks → days → exercises → Exercise.

    Без selectinload каждый GET вытащит 4 + 4×N + 4×N×M запросов; ещё
    одна loop по exercise — N+1 для имени упражнения. Грузим всё одной
    цепочкой selectinload.
    """
    return (
        select(WorkoutPlan)
        .options(
            selectinload(WorkoutPlan.weeks)
            .selectinload(PlanWeek.days)
            .selectinload(PlanDay.exercises)
            .selectinload(PlanExercise.exercise)
        )
    )


async def get_active(
    session: AsyncSession, *, user_id: uuid.UUID
) -> WorkoutPlan | None:
    return (
        await session.execute(
            _select_with_relations().where(
                WorkoutPlan.user_id == user_id,
                WorkoutPlan.status == "active",
            )
        )
    ).scalar_one_or_none()


async def get_by_id(
    session: AsyncSession, *, user_id: uuid.UUID, plan_id: uuid.UUID
) -> WorkoutPlan | None:
    return (
        await session.execute(
            _select_with_relations().where(
                WorkoutPlan.id == plan_id,
                WorkoutPlan.user_id == user_id,
            )
        )
    ).scalar_one_or_none()


async def archive(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    plan_id: uuid.UUID,
    now: datetime | None = None,
) -> WorkoutPlan:
    """Архивирует активный план. 404 → PlanNotFoundError."""
    now = now or datetime.now(UTC)
    plan = await get_by_id(session, user_id=user_id, plan_id=plan_id)
    if plan is None:
        raise PlanNotFoundError()
    if plan.status == "archived":
        return plan
    plan.status = "archived"
    plan.archived_at = now
    await session.flush()
    return plan


async def list_for_user(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[WorkoutPlan], int]:
    where = [WorkoutPlan.user_id == user_id]
    if status is not None:
        where.append(WorkoutPlan.status == status)
    base = select(WorkoutPlan).where(*where)

    count = (
        await session.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await session.execute(
            base.order_by(desc(WorkoutPlan.generated_at))
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return list(rows), int(count)
