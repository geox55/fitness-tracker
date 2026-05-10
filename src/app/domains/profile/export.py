"""GDPR data portability: собрать все данные пользователя в один JSON
(spec 002 NFR-03 + spec 001 REQ-11).

Формат — стабильный, документируемый: при добавлении новых данных дописываем
ключи, не переименовываем существующие. Включаем версию схемы, чтобы клиенты
парсили предсказуемо.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.models import User
from ..inbody.models import InBodyMeasurement
from ..workouts.models import ExerciseLog, Workout
from .models import UserProfile

EXPORT_SCHEMA_VERSION = "1"


def _serialize(value: Any) -> Any:
    """JSON-friendly преобразование для типов SQLAlchemy/Decimal/UUID/datetime."""
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    return value


def _row_to_dict(obj: object, fields: tuple[str, ...]) -> dict[str, Any]:
    return {f: _serialize(getattr(obj, f)) for f in fields}


_USER_FIELDS = ("id", "email", "email_status", "created_at")
_PROFILE_FIELDS = (
    "name",
    "sex",
    "birth_date",
    "height_cm",
    "baseline_weight_kg",
    "goal",
    "target_weight_kg",
    "target_muscle_kg",
    "goal_started_at",
    "training_level",
    "training_frequency",
    "allergies",
    "photo_url",
    "bmr_kcal",
    "onboarding_completed_at",
    "plan_rebuild_required",
    "updated_at",
)
_INBODY_FIELDS = (
    "id",
    "measured_at",
    "weight_kg",
    "height_cm",
    "sex",
    "body_fat_percent",
    "muscle_mass_kg",
    "body_water_percent",
    "protein_kg",
    "minerals_kg",
    "visceral_fat_level",
    "bmr_kcal",
    "fat_free_mass_kg",
    "bmi",
    "source",
    # GDPR-экспорт отдаёт storage-key, а не signed URL: signed URL живёт
    # 5 минут и в архиве потеряет смысл; key достаточно, чтобы клиент мог
    # запросить новую ссылку через API при необходимости.
    "original_pdf_key",
    "created_at",
)
_WORKOUT_FIELDS = (
    "id",
    "performed_at",
    "finished_at",
    "status",
    "origin",
    "notes",
    "created_at",
)
_LOG_FIELDS = (
    "id",
    "workout_id",
    "exercise_id",
    "set_number",
    "reps",
    "weight_kg",
    "rpe",
    "rest_seconds",
    "skipped",
    "logged_at",
)


async def build_export(
    session: AsyncSession, *, user: User
) -> dict[str, Any]:
    profile = await session.get(UserProfile, user.id)

    inbody_stmt = (
        select(InBodyMeasurement)
        .where(InBodyMeasurement.user_id == user.id)
        .order_by(InBodyMeasurement.measured_at)
    )
    measurements = (await session.execute(inbody_stmt)).scalars().all()

    workouts_stmt = (
        select(Workout)
        .where(Workout.user_id == user.id)
        .order_by(Workout.performed_at)
    )
    workouts = (await session.execute(workouts_stmt)).scalars().all()
    workout_ids = [w.id for w in workouts]

    logs: list[ExerciseLog] = []
    if workout_ids:
        logs_stmt = (
            select(ExerciseLog)
            .where(ExerciseLog.workout_id.in_(workout_ids))
            .order_by(ExerciseLog.logged_at)
        )
        logs = list((await session.execute(logs_stmt)).scalars().all())

    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "exported_at": datetime.now(UTC).isoformat(),
        "user": _row_to_dict(user, _USER_FIELDS),
        "profile": (
            _row_to_dict(profile, _PROFILE_FIELDS) if profile is not None else None
        ),
        "inbody_measurements": [
            _row_to_dict(m, _INBODY_FIELDS) for m in measurements
        ],
        "workouts": [_row_to_dict(w, _WORKOUT_FIELDS) for w in workouts],
        "exercise_logs": [_row_to_dict(log, _LOG_FIELDS) for log in logs],
    }
