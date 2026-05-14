"""Сервисный слой избранных упражнений — spec 014.

Чистая логика (`sort_favorites_first`) тестируется без БД. Функции, работающие
с SQLAlchemy-сессией, тонкие — это I/O, а не бизнес-логика.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Exercise, UserExerciseFavorite


async def add_favorite(
    session: AsyncSession, *, user_id: uuid.UUID, exercise_id: uuid.UUID
) -> None:
    """Идемпотентно добавляет упражнение в избранное.

    Использует ON CONFLICT DO NOTHING — повторный POST не падает и не плодит
    дубликатов, не нужно отдельно проверять existence.
    """
    stmt = (
        pg_insert(UserExerciseFavorite)
        .values(user_id=user_id, exercise_id=exercise_id)
        .on_conflict_do_nothing(
            index_elements=[
                UserExerciseFavorite.user_id,
                UserExerciseFavorite.exercise_id,
            ]
        )
    )
    await session.execute(stmt)


async def remove_favorite(
    session: AsyncSession, *, user_id: uuid.UUID, exercise_id: uuid.UUID
) -> None:
    """Идемпотентно убирает упражнение из избранного. Отсутствующая запись —
    не ошибка, метод просто отдаёт None."""
    fav = await session.get(UserExerciseFavorite, (user_id, exercise_id))
    if fav is not None:
        await session.delete(fav)


async def list_favorite_ids(
    session: AsyncSession, *, user_id: uuid.UUID
) -> set[uuid.UUID]:
    """ID-сет избранных. Лёгкая выборка для merge'а с GET /exercises."""
    stmt = select(UserExerciseFavorite.exercise_id).where(
        UserExerciseFavorite.user_id == user_id
    )
    rows = (await session.execute(stmt)).scalars().all()
    return set(rows)


async def list_favorites(
    session: AsyncSession, *, user_id: uuid.UUID
) -> list[Exercise]:
    """Полные упражнения, помеченные пользователем. Сортировка — created_at DESC
    (новые сверху): ожидание пользователя «то, что недавно добавил — в начале»."""
    stmt = (
        select(Exercise)
        .join(
            UserExerciseFavorite,
            UserExerciseFavorite.exercise_id == Exercise.id,
        )
        .where(UserExerciseFavorite.user_id == user_id)
        .order_by(UserExerciseFavorite.created_at.desc())
    )
    return list((await session.execute(stmt)).scalars().all())


# --- Pure helpers (легко тестируются) -------------------------------------


def sort_favorites_first(
    exercises: Iterable[Exercise], favorite_ids: set[uuid.UUID]
) -> list[Exercise]:
    """Стабильная сортировка: сначала избранные (в исходном порядке),
    потом остальные. Используется для in-memory сценариев (тесты, future
    кэш). В production-эндпойнте сортируем на SQL-уровне."""
    favs: list[Exercise] = []
    rest: list[Exercise] = []
    for ex in exercises:
        (favs if ex.id in favorite_ids else rest).append(ex)
    return favs + rest
