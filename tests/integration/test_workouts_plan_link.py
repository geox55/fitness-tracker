"""Integration: spec 005 REQ-12 — связь Workout.plan_day_id.

Проверяем:
- happy path: старт workout с plan_day_id линкует FK + проставляет origin='plan';
- 404 plan_day_not_found если день из чужого плана;
- ON DELETE SET NULL: удаление плана не ломает историю.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.inbody.models import InBodyMeasurement
from app.domains.plan.models import WorkoutPlan
from app.domains.profile.models import UserProfile
from app.domains.workouts.models import Workout
from app.security import create_token


async def _seed_user_with_plan(
    session: AsyncSession, *, email: str
) -> tuple[User, dict[str, str]]:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    session.add(
        UserProfile(
            user_id=user.id,
            sex="male",
            height_cm=Decimal("178"),
            baseline_weight_kg=Decimal("78"),
            goal="muscle_gain",
            training_level="intermediate",
            training_frequency=3,
        )
    )
    session.add(
        InBodyMeasurement(
            user_id=user.id,
            measured_at=datetime.now(UTC),
            weight_kg=Decimal("78"),
            height_cm=Decimal("178"),
            sex="male",
            body_fat_percent=Decimal("18"),
            muscle_mass_kg=Decimal("35"),
            bmi=Decimal("24.6"),
            source="manual",
        )
    )
    # Минимум каталога для composer. Идемпотентно: если в БД уже есть
    # exercise с тем же exercise_id (например, из миграции seed или
    # параллельного теста), пропускаем — uq_exercises_slug не любит дубли.
    existing_slugs = set(
        (
            await session.execute(
                select(Exercise.exercise_id).where(
                    Exercise.exercise_id.in_(
                        [
                            "ex_squat",
                            "ex_bench",
                            "ex_row",
                            "ex_rdl",
                            "ex_ohp",
                            "ex_curl",
                            "ex_plank",
                            "ex_pull",
                            "ex_tri",
                            "ex_glut",
                        ]
                    )
                )
            )
        ).scalars().all()
    )
    for eid, name, primary, equip in [
        ("ex_squat", "Squat", "quads", ["barbell"]),
        ("ex_bench", "Bench", "chest", ["barbell", "bench"]),
        ("ex_row", "Row", "back", ["barbell"]),
        ("ex_rdl", "RDL", "hamstrings", ["barbell"]),
        ("ex_ohp", "OHP", "shoulders", ["barbell"]),
        ("ex_curl", "Curl", "biceps", ["dumbbell"]),
        ("ex_plank", "Plank", "abs", ["bodyweight"]),
        ("ex_pull", "Pullup", "lats", ["pullup_bar"]),
        ("ex_tri", "Tri", "triceps", ["dumbbell"]),
        ("ex_glut", "Hip", "glutes", ["barbell", "bench"]),
    ]:
        if eid in existing_slugs:
            continue
        session.add(
            Exercise(
                exercise_id=eid,
                exercise_name=name,
                primary_muscle_group=primary,
                secondary_muscle_group=[],
                instructions="",
                equipment=equip,
                body_region="upper" if primary != "quads" else "lower",
            )
        )
    await session.commit()

    token, _ = create_token(user_id=user.id, kind="access")
    return user, {"Authorization": f"Bearer {token}"}


async def _generate_plan_via_api(
    client: AsyncClient, headers: dict[str, str]
) -> dict:
    res = await client.post("/api/v1/plans/generate", json={}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


class TestWorkoutPlanLink:
    async def test_start_with_plan_day_sets_link_and_origin(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        _, headers = await _seed_user_with_plan(db_session, email="wp1@example.com")
        plan = await _generate_plan_via_api(client, headers)
        day = plan["weeks"][0]["days"][0]

        res = await client.post(
            "/api/v1/workouts",
            json={"plan_day_id": day["id"]},
            headers=headers,
        )
        assert res.status_code == 201, res.text
        body = res.json()
        assert body["origin"] == "plan"
        assert body["plan_day_id"] == day["id"]

    async def test_start_with_foreign_plan_day_returns_404(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Юзер A создаёт план; юзер B пытается стартовать его день.
        _, headers_a = await _seed_user_with_plan(db_session, email="wp2a@example.com")
        plan_a = await _generate_plan_via_api(client, headers_a)
        day_id = plan_a["weeks"][0]["days"][0]["id"]

        _, headers_b = await _seed_user_with_plan(db_session, email="wp2b@example.com")
        res = await client.post(
            "/api/v1/workouts",
            json={"plan_day_id": day_id},
            headers=headers_b,
        )
        assert res.status_code == 404
        assert res.json()["detail"]["error"] == "plan_day_not_found"

    async def test_freestyle_without_plan_day(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        _, headers = await _seed_user_with_plan(db_session, email="wp3@example.com")
        res = await client.post(
            "/api/v1/workouts",
            json={"origin": "freestyle"},
            headers=headers,
        )
        assert res.status_code == 201
        body = res.json()
        assert body["origin"] == "freestyle"
        assert body["plan_day_id"] is None

    async def test_archived_plan_keeps_link(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # spec 005 §10: история не теряется при архивации плана.
        # FK ON DELETE SET NULL сработает только при физическом DELETE;
        # архивация лишь переключает статус, поэтому link остаётся.
        user, headers = await _seed_user_with_plan(db_session, email="wp4@example.com")
        plan = await _generate_plan_via_api(client, headers)
        day_id = plan["weeks"][0]["days"][0]["id"]

        start = await client.post(
            "/api/v1/workouts",
            json={"plan_day_id": day_id},
            headers=headers,
        )
        workout_id = start.json()["id"]

        # Архивируем план.
        await client.post(
            f"/api/v1/plans/{plan['id']}/archive", headers=headers
        )

        # Workout всё ещё ссылается на plan_day_id.
        workout = (
            await db_session.execute(
                select(Workout).where(Workout.id == uuid.UUID(workout_id))
            )
        ).scalar_one()
        assert workout.plan_day_id is not None
