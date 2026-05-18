"""Integration: фоновые watcher'ы адаптации — spec 009 §2 Scenario 3 +
Scenario 2.3.

Покрытие:
- REQ-02 + Scenario 2.1: PATCH /profile меняет goal → создаётся pending-
  event с trigger=goal_change; идентичный повторный PATCH (debounce из §10)
  не создаёт второй pending. equipment_available меняется → только флаг
  plan_rebuild_required, без события (нет триггера в enum);
- REQ-03 + Scenario 3: активный план с valid_until <= today → /internal/
  adaptation/check-cycles архивирует старый, создаёт новый active и
  пишет cycle_end-событие auto_applied;
- REQ-04 + Scenario 2.3: pending-событие старше 7 дней → тот же эндпоинт
  принудительно перегенерирует план и закрывает событие auto_applied;
- preconditions_not_met у одного пользователя не валит обработку
  остальных (skipped++).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.adaptation.models import PlanRebuildEvent
from app.domains.adaptation.service import run_background_check
from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.inbody.models import InBodyMeasurement
from app.domains.plan.models import WorkoutPlan
from app.domains.profile.models import UserProfile
from app.security import create_token


async def _seed_catalog(session: AsyncSession) -> None:
    """Минимальный пул каталога для composer'а — повторяет test_adaptation_rebuild.py."""
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


async def _onboarded_user(
    session: AsyncSession, *, email: str, goal: str = "muscle_gain"
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
        training_level="intermediate",
        training_frequency=3,
        onboarding_completed_at=datetime.now(UTC),
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


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    token, _ = create_token(user_id=user_id, kind="access")
    return {"Authorization": f"Bearer {token}"}


class TestProfileChangeEvents:
    """REQ-02 + Scenario 2.1: PATCH профиля создаёт pending-event."""

    async def test_goal_change_creates_pending_event(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _onboarded_user(db_session, email="p1@example.com")
        await db_session.commit()

        res = await client.patch(
            "/api/v1/profile",
            json={"goal": "weight_loss"},
            headers=_auth(user.id),
        )
        assert res.status_code == 200, res.text
        assert res.json()["plan_rebuild_required"] is True

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id
                )
            )
        ).scalars().all()
        assert len(events) == 1
        assert events[0].trigger == "goal_change"
        assert events[0].status == "pending"

    async def test_frequency_change_creates_pending_event(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _onboarded_user(db_session, email="p2@example.com")
        await db_session.commit()

        res = await client.patch(
            "/api/v1/profile",
            json={"training_frequency": 5},
            headers=_auth(user.id),
        )
        assert res.status_code == 200, res.text

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id
                )
            )
        ).scalars().all()
        assert len(events) == 1
        assert events[0].trigger == "frequency_change"

    async def test_repeated_goal_change_is_debounced(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Edge case §10: повторная смена цели за один день не создаёт второй
        pending-event."""
        user = await _onboarded_user(db_session, email="p3@example.com")
        await db_session.commit()

        await client.patch(
            "/api/v1/profile",
            json={"goal": "weight_loss"},
            headers=_auth(user.id),
        )
        await client.patch(
            "/api/v1/profile",
            json={"goal": "maintenance"},
            headers=_auth(user.id),
        )

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id,
                    PlanRebuildEvent.status == "pending",
                )
            )
        ).scalars().all()
        # Один pending — флаг уже стоит, второе событие будет шумом.
        assert len(events) == 1
        assert events[0].trigger == "goal_change"

    async def test_equipment_change_sets_flag_without_event(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """equipment_available меняется → флаг есть, события нет (в enum нет
        подходящего триггера, а баннер всё равно покажется по флагу)."""
        user = await _onboarded_user(db_session, email="p4@example.com")
        await db_session.commit()

        res = await client.patch(
            "/api/v1/profile",
            json={"equipment_available": ["dumbbell", "pullup_bar"]},
            headers=_auth(user.id),
        )
        assert res.status_code == 200, res.text
        assert res.json()["plan_rebuild_required"] is True

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id
                )
            )
        ).scalars().all()
        assert events == []


class TestBackgroundCheckCycleEnd:
    """REQ-03 + Scenario 3: просроченный план → авто-регенерация."""

    async def test_expired_plan_is_rebuilt_and_event_logged(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _onboarded_user(db_session, email="c1@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        # Сначала генерим легитимный план через API, потом «вручную» подвигаем
        # valid_until в прошлое — это самое короткое описание «4 недели прошло».
        first = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        assert first.status_code == 201, first.text
        first_plan_id = uuid.UUID(first.json()["id"])

        plan = await db_session.get(WorkoutPlan, first_plan_id)
        assert plan is not None
        plan.valid_until = date.today() - timedelta(days=1)
        await db_session.commit()

        res = await client.post("/api/v1/internal/adaptation/check-cycles")
        assert res.status_code == 200, res.text
        report = res.json()
        assert report["cycle_end_rebuilt"] == 1
        assert report["skipped"] == 0

        active = await client.get(
            "/api/v1/plans/active", headers=_auth(user.id)
        )
        assert active.status_code == 200
        assert uuid.UUID(active.json()["id"]) != first_plan_id

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id
                )
            )
        ).scalars().all()
        # Ретро-событие cycle_end со статусом auto_applied (Scenario 3 идёт
        # без UI-баннера).
        cycle_events = [e for e in events if e.trigger == "cycle_end"]
        assert len(cycle_events) == 1
        assert cycle_events[0].status == "auto_applied"
        assert cycle_events[0].applied_at is not None

    async def test_skips_user_without_preconditions(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Если профиль не дотягивает до preconditions — пользователь идёт в
        skipped, а не валит cron."""
        # Один с просроченным планом и полным профилем, чтобы было что
        # перегенерировать — и убедиться, что батч продолжается.
        ok_user = await _onboarded_user(db_session, email="c2-ok@example.com")
        await _add_inbody(db_session, user_id=ok_user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        first = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(ok_user.id)
        )
        assert first.status_code == 201
        plan = await db_session.get(WorkoutPlan, uuid.UUID(first.json()["id"]))
        assert plan is not None
        plan.valid_until = date.today() - timedelta(days=1)
        await db_session.commit()

        # Второй пользователь — без training_level, но с pending-событием
        # старше 7 дней. Force-rebuild должен сорваться на preconditions.
        bad = User(email="c2-bad@example.com", password_hash="x", email_status="active")
        db_session.add(bad)
        await db_session.flush()
        db_session.add(
            UserProfile(
                user_id=bad.id,
                sex="male",
                height_cm=Decimal("180.0"),
                baseline_weight_kg=Decimal("80.0"),
                goal="muscle_gain",
                # training_level=None  ← не пройдёт preconditions
                training_frequency=3,
                onboarding_completed_at=datetime.now(UTC),
            )
        )
        await db_session.flush()
        db_session.add(
            PlanRebuildEvent(
                user_id=bad.id,
                trigger="goal_change",
                target_plan="workout",
                status="pending",
                triggered_at=datetime.now(UTC) - timedelta(days=8),
            )
        )
        await db_session.commit()

        res = await client.post("/api/v1/internal/adaptation/check-cycles")
        assert res.status_code == 200, res.text
        report = res.json()
        assert report["cycle_end_rebuilt"] == 1
        assert report["skipped"] == 1


class TestBackgroundCheckForceRebuild:
    """REQ-04 + Scenario 2.3: pending-event старше 7 дней → force-rebuild."""

    async def test_old_pending_event_triggers_auto_rebuild(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _onboarded_user(db_session, email="f1@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)
        await db_session.commit()

        first = await client.post(
            "/api/v1/plans/generate", json={}, headers=_auth(user.id)
        )
        assert first.status_code == 201, first.text
        first_plan_id = uuid.UUID(first.json()["id"])

        # Событие старше 7 дней — пользователь проигнорировал баннер.
        db_session.add(
            PlanRebuildEvent(
                user_id=user.id,
                trigger="goal_change",
                target_plan="workout",
                status="pending",
                triggered_at=datetime.now(UTC) - timedelta(days=8),
            )
        )
        await db_session.commit()

        res = await client.post("/api/v1/internal/adaptation/check-cycles")
        assert res.status_code == 200, res.text
        report = res.json()
        assert report["force_rebuilt"] == 1
        # План не просрочен, cycle_end не считается.
        assert report["cycle_end_rebuilt"] == 0

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id
                )
            )
        ).scalars().all()
        assert len(events) == 1
        assert events[0].status == "auto_applied"
        assert events[0].applied_at is not None

        active = await client.get(
            "/api/v1/plans/active", headers=_auth(user.id)
        )
        assert uuid.UUID(active.json()["id"]) != first_plan_id

    async def test_fresh_pending_event_is_not_touched(
        self, db_session: AsyncSession
    ) -> None:
        """Событие младше 7 дней не триггерит force-rebuild — пользователь
        ещё имеет право игнорировать баннер."""
        user = await _onboarded_user(db_session, email="f2@example.com")
        await _add_inbody(db_session, user_id=user.id)
        await _seed_catalog(db_session)

        db_session.add(
            PlanRebuildEvent(
                user_id=user.id,
                trigger="goal_change",
                target_plan="workout",
                status="pending",
                # Свежий event — не должен быть схвачен.
                triggered_at=datetime.now(UTC) - timedelta(days=2),
            )
        )
        await db_session.flush()

        report = await run_background_check(db_session)
        assert report.force_rebuilt == 0
        assert report.cycle_end_rebuilt == 0

        events = (
            await db_session.execute(
                select(PlanRebuildEvent).where(
                    PlanRebuildEvent.user_id == user.id,
                    PlanRebuildEvent.status == "pending",
                )
            )
        ).scalars().all()
        assert len(events) == 1  # остался pending как был
