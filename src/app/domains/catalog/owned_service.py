"""Сервис пользовательских упражнений — spec 014.

`owner_id` на `exercises`: NULL → глобальный каталог, NOT NULL → пользовательский.
Чтение/правка/удаление чужих пользовательских упражнений запрещены — сервис
возвращает None, эндпойнт превращает это в 404 (намеренно не 403, чтобы не
утекало знание о существовании).
"""

from __future__ import annotations

import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Exercise


def _new_custom_exercise_id() -> str:
    """Stable string-id для `exercises.exercise_id` (UNIQUE).
    Префикс `usr_` отличает пользовательские от seed-данных (там короткие
    slug-и из ml/data); 12 hex-символов даёт ~10^14 вариантов — collision-risk
    исчезающе мал для пер-юзерных вставок."""
    return f"usr_{secrets.token_hex(6)}"


async def list_owned(
    session: AsyncSession, *, user_id: uuid.UUID
) -> list[Exercise]:
    """Все упражнения, созданные пользователем. Сортировка — по имени, как
    в основном каталоге, чтобы UX был предсказуемый."""
    stmt = (
        select(Exercise)
        .where(Exercise.owner_id == user_id)
        .order_by(Exercise.exercise_name)
    )
    return list((await session.execute(stmt)).scalars().all())


async def create_owned(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    fields: dict[str, object],
) -> Exercise:
    ex = Exercise(
        exercise_id=_new_custom_exercise_id(),
        owner_id=user_id,
        secondary_muscle_group=list(fields.get("secondary_muscle_group") or []),
        equipment=list(fields.get("equipment") or []),
        # required-поля валидируются Pydantic'ом до сюда; передаём как есть.
        exercise_name=str(fields["exercise_name"]),
        exercise_name_ru=fields.get("exercise_name_ru") or None,  # type: ignore[arg-type]
        primary_muscle_group=str(fields["primary_muscle_group"]),
        body_region=str(fields["body_region"]),
    )
    session.add(ex)
    await session.flush()
    return ex


async def get_owned(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    exercise_id: uuid.UUID,
) -> Exercise | None:
    """Возвращает упражнение, только если это пользовательское и принадлежит
    user_id. Глобальные не трогаем — для них существует отдельный детальный
    GET без проверки владельца."""
    ex = await session.get(Exercise, exercise_id)
    if ex is None or ex.owner_id != user_id:
        return None
    return ex


async def update_owned(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    exercise_id: uuid.UUID,
    changes: dict[str, object],
) -> Exercise | None:
    ex = await get_owned(session, user_id=user_id, exercise_id=exercise_id)
    if ex is None:
        return None
    for field, value in changes.items():
        # Защита от попытки переписать owner_id / exercise_id / id / created_at —
        # `changes` приходит из ExerciseUpdateRequest.model_dump(exclude_unset=True),
        # там этих полей в принципе нет, но дешёвая страховка не помешает.
        if field in {"owner_id", "id", "exercise_id", "created_at"}:
            continue
        setattr(ex, field, value)
    await session.flush()
    return ex


async def delete_owned(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    exercise_id: uuid.UUID,
) -> bool:
    """True — удалили, False — не нашли (или чужое). FK CASCADE на
    user_exercise_favorites автоматически снесёт метку, если она была."""
    ex = await get_owned(session, user_id=user_id, exercise_id=exercise_id)
    if ex is None:
        return False
    await session.delete(ex)
    return True
