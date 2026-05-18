"""Profile endpoints — spec 002.

GET /me — short identity (для шапки и роутинга).
GET / — полный профиль.
PATCH / — частичное обновление (BMR пересчитывается на сервере).
POST /complete-onboarding — фиксация завершения онбординга.
"""

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ...domains.auth.schemas import MeResponse
from ...domains.profile.export import build_export
from ...domains.profile.photo import MAX_BYTES, PhotoError
from ...domains.profile.schemas import ProfileRead, ProfileUpdateRequest
from ...domains.profile.service import (
    IncompleteOnboardingError,
    _extract_key_from_url,
    complete_onboarding,
    delete_photo,
    get_or_create,
    set_photo,
    update_profile,
)
from ...storage import DEFAULT_SIGNED_URL_TTL_SECONDS, Storage, get_storage
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/profile", tags=["profile"])

# Фото профиля живёт в одном bucket с другими аплоадами (приватный после
# spec 013). public_url отдал бы 403 — поэтому при чтении подменяем на
# signed-URL с разумным TTL. Фото читается обычно один раз при загрузке
# экрана; 5 минут хватит, дальше клиент перезапросит /profile.
_PHOTO_TTL = DEFAULT_SIGNED_URL_TTL_SECONDS


def _photo_signed_url(photo_url: str | None, storage: Storage) -> str | None:
    """photo_url из БД — это «исторический» public URL вида
    `<endpoint>/<bucket>/profiles/<uid>/avatar.jpg`. Извлекаем key и
    отдаём короткоживущий signed URL. Если URL не наш (старый external
    URL до spec 013) — оставляем как есть."""
    if photo_url is None:
        return None
    key = _extract_key_from_url(photo_url)
    if key is None:
        return photo_url
    return storage.signed_url(key, ttl_seconds=_PHOTO_TTL)


def _to_read(
    user_email: str, profile: object, *, storage: Storage | None = None
) -> ProfileRead:
    payload = {
        "user_id": profile.user_id,  # type: ignore[attr-defined]
        "email": user_email,
        "name": profile.name,  # type: ignore[attr-defined]
        "sex": profile.sex,  # type: ignore[attr-defined]
        "birth_date": profile.birth_date,  # type: ignore[attr-defined]
        "height_cm": (
            float(profile.height_cm)  # type: ignore[attr-defined]
            if profile.height_cm is not None  # type: ignore[attr-defined]
            else None
        ),
        "baseline_weight_kg": (
            float(profile.baseline_weight_kg)  # type: ignore[attr-defined]
            if profile.baseline_weight_kg is not None  # type: ignore[attr-defined]
            else None
        ),
        "goal": profile.goal,  # type: ignore[attr-defined]
        "target_weight_kg": (
            float(profile.target_weight_kg)  # type: ignore[attr-defined]
            if profile.target_weight_kg is not None  # type: ignore[attr-defined]
            else None
        ),
        "target_muscle_kg": (
            float(profile.target_muscle_kg)  # type: ignore[attr-defined]
            if profile.target_muscle_kg is not None  # type: ignore[attr-defined]
            else None
        ),
        "goal_started_at": profile.goal_started_at,  # type: ignore[attr-defined]
        "training_level": profile.training_level,  # type: ignore[attr-defined]
        "training_frequency": profile.training_frequency,  # type: ignore[attr-defined]
        "allergies": list(profile.allergies),  # type: ignore[attr-defined]
        "equipment_available": (
            list(profile.equipment_available)  # type: ignore[attr-defined]
            if profile.equipment_available is not None  # type: ignore[attr-defined]
            else None
        ),
        "photo_url": _photo_signed_url(
            profile.photo_url,  # type: ignore[attr-defined]
            storage or get_storage(),
        ),
        "bmr_kcal": profile.bmr_kcal,  # type: ignore[attr-defined]
        "onboarding_completed_at": profile.onboarding_completed_at,  # type: ignore[attr-defined]
        "plan_rebuild_required": profile.plan_rebuild_required,  # type: ignore[attr-defined]
        "updated_at": profile.updated_at,  # type: ignore[attr-defined]
    }
    return ProfileRead(**payload)


@router.get("/me", response_model=MeResponse)
async def me(user: CurrentUserDep) -> MeResponse:
    return MeResponse.model_validate(user)


@router.get("", response_model=ProfileRead)
async def get_profile(user: CurrentUserDep, session: SessionDep) -> ProfileRead:
    profile = await get_or_create(session, user_id=user.id)
    return _to_read(user.email, profile)


@router.patch("", response_model=ProfileRead)
async def patch_profile(
    payload: ProfileUpdateRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> ProfileRead:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        # Пустой PATCH — ничего не трогаем, отвечаем текущим состоянием.
        profile = await get_or_create(session, user_id=user.id)
        return _to_read(user.email, profile)
    profile = await update_profile(session, user_id=user.id, changes=changes)
    return _to_read(user.email, profile)


_FILE_DEP = File(...)


@router.post("/photo", response_model=ProfileRead)
async def upload_photo(
    user: CurrentUserDep,
    session: SessionDep,
    file: UploadFile = _FILE_DEP,
) -> ProfileRead:
    raw = await file.read()
    # Двойная проверка размера: starlette в FastAPI принимает до spooled-limit,
    # но мы хотим явный 413 со spec-сообщением, а не ConnectionResetError при
    # превышении.
    if len(raw) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "photo_too_large",
                "message": "Файл больше 5 MB",
            },
        )
    try:
        profile = await set_photo(
            session,
            user_id=user.id,
            raw_bytes=raw,
            storage=get_storage(),
        )
    except PhotoError as exc:
        raise HTTPException(
            status_code=exc.http_status,
            detail={"error": exc.code, "message": str(exc)},
        ) from exc
    return _to_read(user.email, profile)


@router.delete("/photo", response_model=ProfileRead)
async def delete_photo_endpoint(
    user: CurrentUserDep, session: SessionDep
) -> ProfileRead:
    profile = await delete_photo(
        session, user_id=user.id, storage=get_storage()
    )
    return _to_read(user.email, profile)


@router.get("/export")
async def export_my_data(
    user: CurrentUserDep, session: SessionDep
) -> dict[str, Any]:
    """GDPR data portability — единый JSON со всеми данными пользователя."""
    return await build_export(session, user=user)


@router.post("/complete-onboarding", response_model=ProfileRead)
async def post_complete_onboarding(
    user: CurrentUserDep, session: SessionDep
) -> ProfileRead:
    try:
        profile = await complete_onboarding(session, user_id=user.id)
    except IncompleteOnboardingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "incomplete_profile",
                "message": "Заполните обязательные поля профиля",
                "missing_fields": exc.missing,
            },
        ) from exc
    return _to_read(user.email, profile)
