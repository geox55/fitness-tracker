"""Integration: GET /analytics/workouts (тоннаж + число тренировок по периодам)
— spec 010 §3 Scenario 4 / §9, REQ-07/08.

Поднимаем testcontainers Postgres, добавляем Workout + ExerciseLog
напрямую, дёргаем эндпоинт и проверяем агрегаты по неделям/месяцам.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.workouts.models import ExerciseLog, Workout
from app.security import create_token


async def _make_user(session: AsyncSession, *, email: str) -> User:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    return user


async def _ensure_exercise(session: AsyncSession) -> Exercise:
    """Любое упражнение из каталога: id важен только для FK; характеристики
    в этом модуле не проверяем."""
    ex = Exercise(
        exercise_id="bench-press-test",
        exercise_name="Test Bench Press",
        primary_muscle_group="chest",
        secondary_muscle_group=None,
        instructions="test",
        equipment="barbell",
        body_region="upper",
    )
    session.add(ex)
    await session.flush()
    return ex


async def _workout(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    performed_at: datetime,
    status: str = "completed",
) -> Workout:
    w = Workout(
        user_id=user_id,
        performed_at=performed_at,
        finished_at=performed_at,
        status=status,
        origin="freestyle",
    )
    session.add(w)
    await session.flush()
    return w


def _log(
    *,
    workout_id: uuid.UUID,
    exercise_id: uuid.UUID,
    set_number: int,
    reps: int,
    weight_kg: float,
    skipped: bool = False,
) -> ExerciseLog:
    return ExerciseLog(
        workout_id=workout_id,
        exercise_id=exercise_id,
        set_number=set_number,
        reps=reps,
        weight_kg=Decimal(str(weight_kg)),
        skipped=skipped,
    )


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    token, _ = create_token(user_id=user_id, kind="access")
    return {"Authorization": f"Bearer {token}"}


class TestWorkoutsBuckets:
    async def test_groups_by_week_and_aggregates(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # 2 тренировки в одну неделю + 1 в следующую → 2 бакета.
        # Тоннаж в первой = 2*60*100 + 3*8*80 = 12000+1920 = 13920;
        # количество = 2 (тренировки одного дня тоже считаются раздельно).
        user = await _make_user(db_session, email="ws1@example.com")
        ex = await _ensure_exercise(db_session)

        # Понедельник 2026-04-06 и среда 2026-04-08 → одна неделя.
        w1 = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        # NB: формула тоннажа = reps * weight_kg на каждый сет.
        db_session.add(
            _log(
                workout_id=w1.id, exercise_id=ex.id,
                set_number=1, reps=60, weight_kg=100.0,
            )
        )

        w2 = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 8, 10, 0, tzinfo=UTC),
        )
        for s in range(1, 4):  # 3 сета
            db_session.add(
                _log(
                    workout_id=w2.id,
                    exercise_id=ex.id,
                    set_number=s,
                    reps=8,
                    weight_kg=80.0,
                )
            )
        # Тоннаж w2 = 3*8*80 = 1920

        # Следующая неделя — понедельник 2026-04-13.
        w3 = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 13, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(
                workout_id=w3.id, exercise_id=ex.id,
                set_number=1, reps=10, weight_kg=50.0,
            )
        )
        # Тоннаж w3 = 1*10*50 = 500
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=week",
            headers=_auth(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["bucket"] == "week"
        items = body["items"]
        assert len(items) == 2

        first, second = items
        # date_trunc('week') в Postgres — понедельник.
        assert first["period_start"] == "2026-04-06"
        assert first["tonnage_kg"] == 60 * 100 + 3 * 8 * 80  # 7920
        assert first["workouts_count"] == 2

        assert second["period_start"] == "2026-04-13"
        assert second["tonnage_kg"] == 500.0
        assert second["workouts_count"] == 1

    async def test_skipped_logs_excluded_from_tonnage(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Skipped-сет не идёт в тоннаж, но workout всё равно идёт в счётчик.
        user = await _make_user(db_session, email="ws2@example.com")
        ex = await _ensure_exercise(db_session)

        w = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(workout_id=w.id, exercise_id=ex.id, set_number=1,
                 reps=10, weight_kg=100.0, skipped=False)
        )
        db_session.add(
            _log(workout_id=w.id, exercise_id=ex.id, set_number=2,
                 reps=10, weight_kg=100.0, skipped=True)
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=week",
            headers=_auth(user.id),
        )
        item = resp.json()["items"][0]
        # Только non-skipped: 1 * 10 * 100 = 1000.
        assert item["tonnage_kg"] == 1000.0
        assert item["workouts_count"] == 1

    async def test_non_completed_workouts_excluded(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ws3@example.com")
        ex = await _ensure_exercise(db_session)

        # in_progress — не агрегируется (юзер не завершил).
        w_running = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
            status="in_progress",
        )
        db_session.add(
            _log(workout_id=w_running.id, exercise_id=ex.id, set_number=1,
                 reps=10, weight_kg=100.0)
        )
        # cancelled — тоже игнорируется.
        w_cancel = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 7, 10, 0, tzinfo=UTC),
            status="cancelled",
        )
        db_session.add(
            _log(workout_id=w_cancel.id, exercise_id=ex.id, set_number=1,
                 reps=10, weight_kg=100.0)
        )
        # auto_finished — считается (плановое автозакрытие через TTL).
        w_auto = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 8, 10, 0, tzinfo=UTC),
            status="auto_finished",
        )
        db_session.add(
            _log(workout_id=w_auto.id, exercise_id=ex.id, set_number=1,
                 reps=5, weight_kg=60.0)
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=week",
            headers=_auth(user.id),
        )
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["workouts_count"] == 1
        assert items[0]["tonnage_kg"] == 5 * 60.0

    async def test_workout_without_logs_counted_with_zero_tonnage(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Иногда юзер «зашёл, помечает что был» без логов — выдаёт workout
        # без логов; неделя должна показать workouts_count=1, tonnage=0.
        user = await _make_user(db_session, email="ws4@example.com")
        await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=week",
            headers=_auth(user.id),
        )
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["workouts_count"] == 1
        assert items[0]["tonnage_kg"] == 0.0

    async def test_filters_by_from_to_inclusively(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ws5@example.com")
        ex = await _ensure_exercise(db_session)
        for d in (
            datetime(2026, 1, 6, 10, 0, tzinfo=UTC),
            datetime(2026, 2, 16, 10, 0, tzinfo=UTC),
            datetime(2026, 3, 30, 23, 0, tzinfo=UTC),
            datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        ):
            w = await _workout(db_session, user_id=user.id, performed_at=d)
            db_session.add(
                _log(workout_id=w.id, exercise_id=ex.id, set_number=1,
                     reps=10, weight_kg=50.0)
            )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=week"
            "&from=2026-02-01&to=2026-03-30",
            headers=_auth(user.id),
        )
        items = resp.json()["items"]
        # Внутри диапазона — фев и март-30 (последний день включительно).
        starts = [it["period_start"] for it in items]
        assert "2026-02-16" in starts
        assert "2026-03-30" in starts
        assert "2026-01-06" not in starts
        assert "2026-04-06" not in starts

    async def test_bucket_month(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ws-month@example.com")
        ex = await _ensure_exercise(db_session)
        for d in (
            datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
            datetime(2026, 1, 25, 10, 0, tzinfo=UTC),
            datetime(2026, 2, 10, 10, 0, tzinfo=UTC),
        ):
            w = await _workout(db_session, user_id=user.id, performed_at=d)
            db_session.add(
                _log(workout_id=w.id, exercise_id=ex.id, set_number=1,
                     reps=10, weight_kg=50.0)
            )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=month",
            headers=_auth(user.id),
        )
        items = resp.json()["items"]
        assert len(items) == 2
        assert items[0]["period_start"] == "2026-01-01"
        assert items[0]["workouts_count"] == 2
        assert items[1]["period_start"] == "2026-02-01"
        assert items[1]["workouts_count"] == 1

    async def test_unsupported_bucket_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ws-bad@example.com")
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=year",
            headers=_auth(user.id),
        )
        assert resp.status_code == 400
        assert resp.json()["detail"]["error"] == "unsupported_bucket"

    async def test_inverted_range_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ws-range@example.com")
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=week"
            "&from=2026-03-01&to=2026-02-01",
            headers=_auth(user.id),
        )
        assert resp.status_code == 400
        assert resp.json()["detail"]["error"] == "invalid_range"

    async def test_other_users_workouts_not_visible(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Базовая проверка изоляции: тренировки соседа не считаются.
        alice = await _make_user(db_session, email="ws-alice@example.com")
        bob = await _make_user(db_session, email="ws-bob@example.com")
        ex = await _ensure_exercise(db_session)
        w = await _workout(
            db_session, user_id=bob.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(workout_id=w.id, exercise_id=ex.id, set_number=1,
                 reps=10, weight_kg=100.0)
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/workouts?bucket=week",
            headers=_auth(alice.id),
        )
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    async def test_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/analytics/workouts")
        assert resp.status_code == 401
