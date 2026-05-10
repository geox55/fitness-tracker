"""Бизнес-операции профиля: автопересчёт BMR, флаг pending-rebuild, онбординг.

Чистый слой поверх SQLAlchemy: ничего из FastAPI здесь нет, чтобы тесты могли
дёргать функции напрямую.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.calc.bmr import bmr_mifflin_st_jeor
from .models import UserProfile

# Поля, без которых нельзя завершить онбординг (REQ-02).
REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "sex",
    "birth_date",
    "height_cm",
    "baseline_weight_kg",
    "goal",
    "training_level",
    "training_frequency",
)

# Изменение этих полей сбрасывает плановый блок: AI-генератор должен пересобрать
# план тренировок (REQ-10, см. spec 009).
PLAN_INVALIDATING_FIELDS: frozenset[str] = frozenset({"goal", "training_frequency"})

# Поля, влияющие на BMR (Mifflin-St Jeor) — REQ-11.
BMR_INPUT_FIELDS: frozenset[str] = frozenset(
    {"sex", "birth_date", "height_cm", "baseline_weight_kg"}
)


class ProfileError(Exception):
    code: str = "profile_error"


class IncompleteOnboardingError(ProfileError):
    code = "incomplete_profile"

    def __init__(self, missing: list[str]) -> None:
        super().__init__(f"missing required fields: {missing}")
        self.missing = missing


def _years_between(start: date, end: date) -> int:
    return end.year - start.year - ((end.month, end.day) < (start.month, start.day))


def _maybe_recalc_bmr(profile: UserProfile) -> None:
    """Пересчитать BMR, если все необходимые входы есть.

    Если каких-то входов нет (онбординг не закончен) — оставляем None и не
    падаем: пользователь имеет право заполнять профиль постепенно.
    """
    needed = (
        profile.sex,
        profile.birth_date,
        profile.height_cm,
        profile.baseline_weight_kg,
    )
    if any(v is None for v in needed):
        profile.bmr_kcal = None
        return
    age = _years_between(profile.birth_date, date.today())  # type: ignore[arg-type]
    weight = float(profile.baseline_weight_kg)  # type: ignore[arg-type]
    height = float(profile.height_cm)  # type: ignore[arg-type]
    profile.bmr_kcal = round(
        bmr_mifflin_st_jeor(
            weight_kg=weight,
            height_cm=height,
            age_years=age,
            sex=profile.sex,  # type: ignore[arg-type]
        )
    )


async def get_or_create(
    session: AsyncSession, *, user_id: uuid.UUID
) -> UserProfile:
    """Возвращает существующий профиль или создаёт пустой (после регистрации
    профиль гарантированно есть только после первого PATCH)."""
    profile = await session.get(UserProfile, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id)
        session.add(profile)
        await session.flush()
    return profile


def _coerce_for_storage(field: str, value: Any) -> Any:
    """Числовые поля храним как Decimal, остальное — как есть."""
    if value is None:
        return None
    if field in {
        "height_cm",
        "baseline_weight_kg",
        "target_weight_kg",
        "target_muscle_kg",
    }:
        return Decimal(str(value))
    return value


def apply_changes(profile: UserProfile, changes: dict[str, Any]) -> None:
    """Чистая логика применения PATCH-патча без обращения к БД.

    Меняет переданный объект in-place: пишет новые значения, пересчитывает
    BMR при изменении любого его входа, и поднимает plan_rebuild_required,
    если у уже-онбордившегося пользователя поменялись цель или частота.
    """
    bmr_inputs_changed = False
    plan_dirty = False

    for field, raw in changes.items():
        new_value = _coerce_for_storage(field, raw)
        old_value = getattr(profile, field)
        if old_value == new_value:
            continue
        setattr(profile, field, new_value)
        if field in BMR_INPUT_FIELDS:
            bmr_inputs_changed = True
        if field in PLAN_INVALIDATING_FIELDS and profile.onboarding_completed_at:
            # До завершения онбординга план ещё не сгенерирован — флагать нечего.
            plan_dirty = True

    if bmr_inputs_changed:
        _maybe_recalc_bmr(profile)
    if plan_dirty:
        profile.plan_rebuild_required = True


async def update_profile(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    changes: dict[str, Any],
) -> UserProfile:
    profile = await get_or_create(session, user_id=user_id)
    apply_changes(profile, changes)
    await session.flush()
    return profile


def missing_required_fields(profile: UserProfile) -> list[str]:
    return [f for f in REQUIRED_FIELDS if getattr(profile, f) is None]


async def set_photo(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    raw_bytes: bytes,
    storage: Any,
) -> UserProfile:
    """Принять загруженный файл, провалидировать, ресайзить, положить в storage,
    обновить photo_url. Если у пользователя был старый photo — удаляется."""
    from .photo import process_image, validate_image_bytes

    image = validate_image_bytes(raw_bytes)
    processed = process_image(image)

    profile = await get_or_create(session, user_id=user_id)
    new_key = f"profiles/{user_id}/avatar.jpg"
    new_url = await storage.put(
        key=new_key, data=processed, content_type="image/jpeg"
    )

    # Старое фото удаляем после успешной заливки нового, но до коммита —
    # если упадём, в худшем случае останется orphan-объект, не сломанный URL.
    old_url = profile.photo_url
    profile.photo_url = new_url
    await session.flush()

    if old_url and old_url != new_url:
        old_key = _extract_key_from_url(old_url)
        if old_key:
            await storage.delete(key=old_key)

    return profile


async def delete_photo(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    storage: Any,
) -> UserProfile:
    profile = await get_or_create(session, user_id=user_id)
    if profile.photo_url:
        old_key = _extract_key_from_url(profile.photo_url)
        if old_key:
            await storage.delete(key=old_key)
        profile.photo_url = None
        await session.flush()
    return profile


def _extract_key_from_url(url: str) -> str | None:
    """Из публичного URL восстановить storage key вида `profiles/<uid>/avatar.jpg`.

    Логика проста: ключ начинается там, где заканчивается basename бакета.
    Если URL не наш (например, после миграции из другой системы) — возвращаем
    None, и старый объект остаётся orphan'ом.
    """
    marker = "/profiles/"
    idx = url.find(marker)
    if idx < 0:
        return None
    return url[idx + 1 :]


async def complete_onboarding(
    session: AsyncSession, *, user_id: uuid.UUID
) -> UserProfile:
    profile = await get_or_create(session, user_id=user_id)
    missing = missing_required_fields(profile)
    if missing:
        raise IncompleteOnboardingError(missing)
    if profile.onboarding_completed_at is None:
        profile.onboarding_completed_at = datetime.now(UTC)
    # На всякий случай гарантируем актуальный BMR на момент завершения.
    _maybe_recalc_bmr(profile)
    await session.flush()
    return profile
