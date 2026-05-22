"""Integration: spec 015 REQ-01/02 — idempotency POST'ов по client_id.

Проверяем что повторный POST с тем же client_id (имитация offline-retry
после потерянного ответа) не создаёт дубликата, а возвращает существующую
запись с тем же server-side ID.

Покрытые эндпоинты:
- POST /workouts                  (start_workout)
- POST /workouts/{id}/logs        (log_set)
- POST /inbody/measurements       (create_manual via inbody.service)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.inbody.models import InBodyMeasurement
from app.domains.profile.models import UserProfile
from app.domains.workouts.models import ExerciseLog, Workout
from app.security import create_token


async def _seed_user(
    session: AsyncSession, *, email: str
) -> tuple[User, dict[str, str]]:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    session.add(
        UserProfile(
            user_id=user.id,
            sex="female",
            height_cm=Decimal("165"),
            baseline_weight_kg=Decimal("60"),
            goal="maintenance",
            training_level="intermediate",
            training_frequency=3,
        )
    )
    await session.commit()

    token, _ = create_token(user_id=user.id, kind="access")
    return user, {"Authorization": f"Bearer {token}"}


async def _ensure_exercise(session: AsyncSession) -> uuid.UUID:
    """Гарантирует наличие хотя бы одного упражнения в каталоге."""
    existing = await session.scalar(
        select(Exercise).where(Exercise.exercise_id == "ex_test_idem")
    )
    if existing is not None:
        return existing.id
    ex = Exercise(
        exercise_id="ex_test_idem",
        exercise_name="Idem Test Ex",
        primary_muscle_group="chest",
        secondary_muscle_group=[],
        instructions="",
        equipment=["bodyweight"],
        body_region="upper",
    )
    session.add(ex)
    await session.commit()
    return ex.id


class TestWorkoutIdempotency:
    async def test_repeated_post_with_same_client_id_returns_existing(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        _, headers = await _seed_user(db_session, email="idem-w1@example.com")
        client_id = str(uuid.uuid4())

        r1 = await client.post(
            "/api/v1/workouts",
            json={"origin": "freestyle", "client_id": client_id},
            headers=headers,
        )
        assert r1.status_code == 201, r1.text
        first_id = r1.json()["id"]

        r2 = await client.post(
            "/api/v1/workouts",
            json={"origin": "freestyle", "client_id": client_id},
            headers=headers,
        )
        # Идемпотентный повтор: тот же ID, без 409 active_workout_exists.
        assert r2.status_code in (200, 201), r2.text
        assert r2.json()["id"] == first_id

        # В БД ровно одна запись с этим client_id.
        cnt = await db_session.scalar(
            select(func.count())
            .select_from(Workout)
            .where(Workout.client_id == uuid.UUID(client_id))
        )
        assert cnt == 1

    async def test_post_without_client_id_creates_distinct_records(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        _, headers = await _seed_user(db_session, email="idem-w2@example.com")

        r1 = await client.post(
            "/api/v1/workouts",
            json={"origin": "freestyle"},
            headers=headers,
        )
        assert r1.status_code == 201
        # Заканчиваем активную, чтобы можно было создать вторую.
        await client.post(
            f"/api/v1/workouts/{r1.json()['id']}/cancel", headers=headers
        )
        r2 = await client.post(
            "/api/v1/workouts",
            json={"origin": "freestyle"},
            headers=headers,
        )
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]


class TestExerciseLogIdempotency:
    async def test_repeated_log_with_same_client_id_returns_existing(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        _, headers = await _seed_user(db_session, email="idem-l1@example.com")
        ex_id = await _ensure_exercise(db_session)

        # Стартуем тренировку.
        r_w = await client.post(
            "/api/v1/workouts", json={"origin": "freestyle"}, headers=headers
        )
        wid = r_w.json()["id"]

        client_id = str(uuid.uuid4())
        payload = {
            "exercise_id": str(ex_id),
            "set_number": 1,
            "reps": 10,
            "weight_kg": 20,
            "rpe": 7,
            "client_id": client_id,
        }
        r1 = await client.post(
            f"/api/v1/workouts/{wid}/logs", json=payload, headers=headers
        )
        assert r1.status_code == 201, r1.text
        first_log_id = r1.json()["id"]

        # Retry — ожидаем тот же лог.
        r2 = await client.post(
            f"/api/v1/workouts/{wid}/logs", json=payload, headers=headers
        )
        assert r2.status_code in (200, 201), r2.text
        assert r2.json()["id"] == first_log_id

        cnt = await db_session.scalar(
            select(func.count())
            .select_from(ExerciseLog)
            .where(ExerciseLog.client_id == uuid.UUID(client_id))
        )
        assert cnt == 1


class TestInBodyIdempotency:
    async def test_repeated_inbody_with_same_client_id_returns_existing(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        _, headers = await _seed_user(db_session, email="idem-i1@example.com")
        client_id = str(uuid.uuid4())
        payload = {
            "measured_at": datetime.now(UTC).isoformat(),
            "weight_kg": 60.0,
            "body_fat_percent": 22.0,
            "muscle_mass_kg": 25.0,
            "client_id": client_id,
        }
        r1 = await client.post(
            "/api/v1/inbody/measurements", json=payload, headers=headers
        )
        assert r1.status_code == 201, r1.text
        first_id = r1.json()["id"]

        r2 = await client.post(
            "/api/v1/inbody/measurements", json=payload, headers=headers
        )
        # Существующая запись (без HTTP 409 / 500).
        assert r2.status_code in (200, 201), r2.text
        assert r2.json()["id"] == first_id

        cnt = await db_session.scalar(
            select(func.count())
            .select_from(InBodyMeasurement)
            .where(InBodyMeasurement.client_id == uuid.UUID(client_id))
        )
        assert cnt == 1
