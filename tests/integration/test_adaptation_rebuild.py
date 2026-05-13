"""Integration: /plans/rebuild — spec 009 §2 Scenario 2.2.

Покрытие:
- happy path: pending-event + полный профиль → 201, event=user_confirmed,
  свежий план active, прошлый archived;
- без pending-event: создаётся manual-event и тоже user_confirmed после
  успешной генерации (Scenario 2.2 без баннера — пользователь сам пришёл);
- preconditions_not_met: 400, событие НЕ помечается user_confirmed
  (остаётся pending) — аудит не должен лгать.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.adaptation.models import PlanRebuildEvent
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
) -> User:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    profile = UserProfile(
        user_id=user.id,
        sex="male",
        height_cm=Decimal("178.0"),
        baseline_weight_kg=Decimal("78.0"),
        goal=goal,
        training_level=level,
        training_frequency=frequency,
    )
    session.add(profile)
    await session.flush()
    return user


async def _add_inbody(session: AsyncSession, *, user_id: uuid.UUID) -> None:
    session.add(
        InBodyMeasurement(
            user_id=user_id,
            measured_at=datetime.now(UTC),
            weight_kg=Decimal("78.0"),
            height_cm=Decimal("178.0"),
            sex="male",
            body_fat_percent=Decimal("18.0"),
            muscle_mass_kg=Decimal("35.0"),
            bmi=Decimal("24.6"),
            source="manual",
        )
    )
    await session.flush()


async def _seed_catalog(session: AsyncSession) -> None:
    """Минимальный пул каталога для composer'а — повторяет test_plans.py."""
    rows = [
        ("ex_squat", "Присед", "quads", ["glutes"], ["barbell"], "lower"),
        ("ex_bench", "Жим лёжа", "chest", ["triceps"], ["barbell", "bench"], "upper"),
        ("ex_row", "Тяга штанги", "back", ["biceps"], ["barbell"], "upper"),
        ("ex_rdl", "РТТ", "hamstrings", ["glutes"], ["barbell"], "lower"),
        ("ex_ohp", "Армейский", "shoulders", ["triceps"], ["barbell"], "upper"),
        ("ex_pullup", "Подтягивания", "lats", ["biceps"], ["pullup_bar"], "upper"),
        ("ex_curl", "Сгибания", "biceps", [], ["dumbbell"], "upper"),
        ("ex_plank", "Планка", "abs", [], ["bodyweight"], "core"),
        ("ex_hip", "Ягодичный мост", "glutes", ["hamstrings"], ["barbell", "bench"], "lower"),
        ("ex_tri", "Разгибание трицепса", "triceps", [], ["dumbbell"], "upper"),
    ]
    for eid, name_ru, primary, secondary, equipment, region in rows:
        session.add(
            Exercise(
                exercise_id=eid,
                exercise_name=eid,
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


class TestRebuildPlan:
    async def test_rebuild_consumes_pending_event_and_archives_old_plan(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Scenario 2.2 happy path: pending → user_confirmed + новый active."""
        user = await _user_with_profile(db_session, email="r1@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)

        # Прошлый план + pending-event как у баннера «План устарел».
        first = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        assert first.status_code == 201, first.text
        first_plan_id = first.json()["id"]

        db_session.add(
            PlanRebuildEvent(
                user_id=user.id,
                trigger="goal_change",
                target_plan="workout",
                status="pending",
                triggered_at=datetime.now(UTC),
            )
        )
        await db_session.commit()

        res = await client.post(
            "/api/v1/plans/rebuild",
            json={"target": "workout"},
            headers=_auth(user.id),
        )
        assert res.status_code == 201, res.text
        body = res.json()
        assert body["status"] == "user_confirmed"
        assert body["target_plan"] == "workout"
        assert body["plan_id"] != first_plan_id

        # Старый план — archived; новый — active.
        active = await client.get(
            "/api/v1/plans/active", headers=_auth(user.id)
        )
        assert active.status_code == 200
        assert active.json()["id"] == body["plan_id"]

        old = await client.get(
            f"/api/v1/plans/{first_plan_id}", headers=_auth(user.id)
        )
        assert old.status_code == 200
        assert old.json()["status"] == "archived"

        # Событие из БД помечено user_confirmed + applied_at.
        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id
                )
            )
        ).scalars().all()
        assert len(events) == 1
        assert events[0].status == "user_confirmed"
        assert events[0].applied_at is not None
        assert events[0].trigger == "goal_change"

    async def test_rebuild_without_pending_event_creates_manual_one(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Пользователь нажал «Обновить» из настроек без баннера —
        фиксируем как manual-событие в аудите."""
        user = await _user_with_profile(db_session, email="r2@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        res = await client.post(
            "/api/v1/plans/rebuild",
            json={"target": "workout"},
            headers=_auth(user.id),
        )
        assert res.status_code == 201, res.text
        assert res.json()["status"] == "user_confirmed"

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id
                )
            )
        ).scalars().all()
        assert len(events) == 1
        assert events[0].trigger == "manual"
        assert events[0].status == "user_confirmed"

    async def test_rebuild_preconditions_not_met_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """REQ-01 spec 006: профиль не заполнен — `/plans/rebuild`
        мапится на ту же 400 `preconditions_not_met`, что и
        `/plans/generate`. PWA-клиент использует один обработчик.

        Поведение «событие остаётся pending» проверяется на уровне
        unit-теста сервиса — после 400 override-сессия откачивается,
        и дополнительные операции в том же тесте словили бы
        MissingGreenlet (общая для коллекции тестов идиома: проверяем
        только сам ответ).
        """
        user = await _user_with_profile(
            db_session,
            email="r3@example.com",
            goal=None,
            level=None,
            frequency=None,
        )
        await db_session.commit()

        res = await client.post(
            "/api/v1/plans/rebuild",
            json={"target": "workout"},
            headers=_auth(user.id),
        )
        assert res.status_code == 400
        detail = res.json()["detail"]
        assert detail["error"] == "preconditions_not_met"
        assert set(detail["missing"]) == {
            "goal",
            "training_level",
            "training_frequency",
        }
