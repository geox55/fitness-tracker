"""Бизнес-операции InBody: BMI-автосчёт, снапшот роста/пола из профиля.

Чистые helpers (compute_bmi, build_measurement) тестируются без БД.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..profile.models import UserProfile
from .models import InBodyMeasurement


class InBodyError(Exception):
    code: str = "inbody_error"


class HeightUnknownError(InBodyError):
    """Рост не передан и не сохранён в профиле — нечего записывать в снапшот."""

    code = "height_required"


class SexUnknownError(InBodyError):
    """Аналогично для пола."""

    code = "sex_required"


def compute_bmi(weight_kg: Decimal, height_cm: Decimal) -> Decimal:
    """BMI = weight / (height_m^2). Округление до 0.1 для UI и graphs."""
    if height_cm <= 0:
        raise ValueError("height_cm must be positive")
    height_m = height_cm / Decimal(100)
    bmi = weight_kg / (height_m * height_m)
    return bmi.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def _to_decimal(value: float | int | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def build_measurement(
    *,
    user_id: uuid.UUID,
    payload: dict[str, Any],
    profile_height_cm: Decimal | None,
    profile_sex: str | None,
    source: str = "manual",
) -> InBodyMeasurement:
    """Собрать ORM-объект, подставив рост/пол из профиля, если их нет в payload.

    Не работает с сессией — это чистая функция; вызывающий код добавляет
    результат в session.add(). Так удобно тестировать без БД.
    """
    height = _to_decimal(payload.get("height_cm")) or profile_height_cm
    if height is None:
        raise HeightUnknownError(
            "height_cm not provided and not present in user profile"
        )
    sex = payload.get("sex") or profile_sex
    if sex is None:
        raise SexUnknownError(
            "sex not provided and not present in user profile"
        )

    weight = _to_decimal(payload["weight_kg"])
    assert weight is not None  # уже валидировано Pydantic'ом
    bmi = compute_bmi(weight, height)

    return InBodyMeasurement(
        user_id=user_id,
        measured_at=payload["measured_at"],
        weight_kg=weight,
        height_cm=height,
        sex=sex,
        body_fat_percent=_to_decimal(payload["body_fat_percent"]),
        muscle_mass_kg=_to_decimal(payload.get("muscle_mass_kg")),
        body_water_percent=_to_decimal(payload.get("body_water_percent")),
        protein_kg=_to_decimal(payload.get("protein_kg")),
        minerals_kg=_to_decimal(payload.get("minerals_kg")),
        visceral_fat_level=payload.get("visceral_fat_level"),
        bmr_kcal=payload.get("bmr_kcal"),
        fat_free_mass_kg=_to_decimal(payload.get("fat_free_mass_kg")),
        bmi=bmi,
        source=source,
        original_pdf_url=payload.get("original_pdf_url"),
    )


async def create_manual(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    payload: dict[str, Any],
) -> InBodyMeasurement:
    profile = await session.get(UserProfile, user_id)
    measurement = build_measurement(
        user_id=user_id,
        payload=payload,
        profile_height_cm=profile.height_cm if profile else None,
        profile_sex=profile.sex if profile else None,
        source="manual",
    )
    session.add(measurement)
    await session.flush()
    return measurement


async def list_for_user(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    limit: int,
    offset: int,
) -> tuple[list[InBodyMeasurement], int]:
    items_stmt = (
        select(InBodyMeasurement)
        .where(InBodyMeasurement.user_id == user_id)
        .order_by(InBodyMeasurement.measured_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = (await session.execute(items_stmt)).scalars().all()
    total = (
        await session.execute(
            select(func.count(InBodyMeasurement.id)).where(
                InBodyMeasurement.user_id == user_id
            )
        )
    ).scalar_one()
    return list(items), int(total)


async def get_for_user(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    measurement_id: uuid.UUID,
) -> InBodyMeasurement | None:
    stmt = select(InBodyMeasurement).where(
        InBodyMeasurement.id == measurement_id,
        InBodyMeasurement.user_id == user_id,
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def delete(
    session: AsyncSession, measurement: InBodyMeasurement
) -> None:
    await session.delete(measurement)


async def latest_measured_at(
    session: AsyncSession, *, user_id: uuid.UUID
) -> datetime | None:
    stmt = (
        select(InBodyMeasurement.measured_at)
        .where(InBodyMeasurement.user_id == user_id)
        .order_by(InBodyMeasurement.measured_at.desc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()
