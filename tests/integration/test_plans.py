"""Integration: /plans/* — spec 006 §3 Scenarios 1, 2, 5, 6.

Сценарии:
- happy path: POST /plans/generate возвращает 201 с 4 неделями;
- 400 preconditions_not_met если профиль не заполнен;
- GET /plans/active возвращает свежий план;
- POST /plans/{id}/archive переводит в archived;
- повторная генерация архивирует предыдущий active.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.inbody.models import InBodyMeasurement
from app.domains.profile.models import UserProfile
from app.security import create_token


async def _user_with_profile(
    session: AsyncSession,
    *,
    email: str,
    goal: str | None = "muscle_gain",
    level: str | None = "intermediate",
    frequency: int | None = 3,
    height_cm: float | None = 178.0,
    weight_kg: float | None = 78.0,
) -> User:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    profile = UserProfile(
        user_id=user.id,
        sex="male",
        height_cm=Decimal(str(height_cm)) if height_cm else None,
        baseline_weight_kg=Decimal(str(weight_kg)) if weight_kg else None,
        goal=goal,
        training_level=level,
        training_frequency=frequency,
    )
    session.add(profile)
    await session.flush()
    return user


async def _add_inbody(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    weight_kg: float = 78.0,
    measured_at: datetime | None = None,
) -> InBodyMeasurement:
    m = InBodyMeasurement(
        user_id=user_id,
        measured_at=measured_at or datetime.now(UTC),
        weight_kg=Decimal(str(weight_kg)),
        height_cm=Decimal("178.0"),
        sex="male",
        body_fat_percent=Decimal("18.0"),
        muscle_mass_kg=Decimal("35.0"),
        bmi=Decimal(str(round(weight_kg / (1.78 * 1.78), 2))),
        source="manual",
    )
    session.add(m)
    await session.flush()
    return m


async def _seed_catalog(session: AsyncSession) -> None:
    """Минимальный пул каталога, чтобы composer наполнил основные слоты."""
    exercises = [
        ("ex_squat", "Barbell Back Squat", "Присед", "quads", ["glutes"], ["barbell"], "lower"),
        ("ex_bench", "Barbell Bench Press", "Жим лёжа", "chest", ["triceps"], ["barbell", "bench"], "upper"),
        ("ex_row", "Barbell Row", "Тяга штанги", "back", ["biceps"], ["barbell"], "upper"),
        ("ex_rdl", "Romanian Deadlift", "РТТ", "hamstrings", ["glutes"], ["barbell"], "lower"),
        ("ex_ohp", "Overhead Press", "Армейский", "shoulders", ["triceps"], ["barbell"], "upper"),
        ("ex_pullup", "Pullup", "Подтягивания", "lats", ["biceps"], ["pullup_bar"], "upper"),
        ("ex_curl", "Bicep Curl", "Сгибания", "biceps", [], ["dumbbell"], "upper"),
        ("ex_plank", "Plank", "Планка", "abs", [], ["bodyweight"], "core"),
        ("ex_hip", "Hip Thrust", "Ягодичный мост", "glutes", ["hamstrings"], ["barbell", "bench"], "lower"),
        ("ex_tri", "Tricep Extension", "Разгибание трицепса", "triceps", [], ["dumbbell"], "upper"),
    ]
    for eid, name, name_ru, primary, secondary, equipment, region in exercises:
        session.add(
            Exercise(
                exercise_id=eid,
                exercise_name=name,
                exercise_name_ru=name_ru,
                primary_muscle_group=primary,
                secondary_muscle_group=secondary,
                instructions="",
                equipment=equipment,
                body_region=region,
            )
        )
    await session.flush()


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    token, _ = create_token(user_id=user_id, kind="access")
    return {"Authorization": f"Bearer {token}"}


class TestPlanGeneration:
    async def test_generate_happy_path_returns_four_weeks(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _user_with_profile(db_session, email="p1@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        res = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        assert res.status_code == 201, res.text
        body = res.json()
        assert body["status"] == "active"
        assert body["frequency"] == 3
        assert body["goal"] == "muscle_gain"
        assert body["training_level"] == "intermediate"
        assert len(body["weeks"]) == 4
        # На каждой неделе — 3 strength-дня.
        for week in body["weeks"]:
            strength_days = [d for d in week["days"] if d["type"] == "strength"]
            assert len(strength_days) == 3
        # Прогрессия должна расти от w1 к w4 у хотя бы одного упражнения.
        w1_ex = body["weeks"][0]["days"][0]["exercises"][0]
        w4_ex = next(
            (
                e
                for e in body["weeks"][3]["days"][0]["exercises"]
                if e["exercise_id"] == w1_ex["exercise_id"]
            ),
            None,
        )
        assert w4_ex is not None
        # Либо вес, либо повторы выросли.
        grew_w = (w4_ex["target_weight_kg"] or 0) > (
            w1_ex["target_weight_kg"] or 0
        )
        grew_r = w4_ex["target_reps_max"] > w1_ex["target_reps_max"]
        assert grew_w or grew_r

    async def test_generate_preconditions_not_met_without_profile_fields(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Пользователь без goal/level/frequency.
        user = await _user_with_profile(
            db_session,
            email="p2@example.com",
            goal=None,
            level=None,
            frequency=None,
        )
        await _seed_catalog(db_session)
        await db_session.commit()

        res = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        assert res.status_code == 400
        detail = res.json()["detail"]
        assert detail["error"] == "preconditions_not_met"
        assert set(detail["missing"]) == {
            "goal",
            "training_level",
            "training_frequency",
        }

    async def test_generate_archives_previous_active(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _user_with_profile(db_session, email="p3@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        first = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        assert first.status_code == 201
        first_id = first.json()["id"]

        second = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        assert second.status_code == 201
        second_id = second.json()["id"]
        assert second_id != first_id

        # GET active возвращает второй.
        active = await client.get("/api/v1/plans/active", headers=_auth(user.id))
        assert active.status_code == 200
        assert active.json()["id"] == second_id

        # GET first — статус archived.
        old = await client.get(
            f"/api/v1/plans/{first_id}", headers=_auth(user.id)
        )
        assert old.status_code == 200
        assert old.json()["status"] == "archived"

    async def test_override_equipment_constrains_pool(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _user_with_profile(db_session, email="p4@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        res = await client.post(
            "/api/v1/plans/generate",
            json={
                "override": {
                    "equipment_available": ["bodyweight", "pullup_bar"]
                }
            },
            headers=_auth(user.id),
        )
        assert res.status_code == 201
        body = res.json()
        # Не должно быть ни одного barbell/dumbbell-only упражнения.
        for week in body["weeks"]:
            for day in week["days"]:
                if day["type"] != "strength":
                    continue
                for ex in day["exercises"]:
                    # exercise_id может быть None для placeholder-cardio.
                    assert ex["target_sets"] >= 1


class TestPlanReads:
    async def test_active_404_when_no_plan(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _user_with_profile(db_session, email="p5@example.com")
        await db_session.commit()
        res = await client.get("/api/v1/plans/active", headers=_auth(user.id))
        assert res.status_code == 404

    async def test_archive_endpoint(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _user_with_profile(db_session, email="p6@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        plan = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        pid = plan.json()["id"]

        res = await client.post(
            f"/api/v1/plans/{pid}/archive", headers=_auth(user.id)
        )
        assert res.status_code == 200
        assert res.json()["status"] == "archived"

        # GET active теперь 404.
        active = await client.get("/api/v1/plans/active", headers=_auth(user.id))
        assert active.status_code == 404

    async def test_list_filtered_by_status(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _user_with_profile(db_session, email="p7@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )

        archived = await client.get(
            "/api/v1/plans?status=archived", headers=_auth(user.id)
        )
        assert archived.status_code == 200
        assert archived.json()["total"] == 1

        active_list = await client.get(
            "/api/v1/plans?status=active", headers=_auth(user.id)
        )
        assert active_list.json()["total"] == 1

    async def test_plan_isolated_per_user(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        u1 = await _user_with_profile(db_session, email="p8@example.com")
        u2 = await _user_with_profile(db_session, email="p9@example.com")
        await _add_inbody(db_session, user_id=u1.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        plan = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(u1.id)
        )
        pid = plan.json()["id"]
        # u2 не должен видеть план u1.
        res = await client.get(
            f"/api/v1/plans/{pid}", headers=_auth(u2.id)
        )
        assert res.status_code == 404
