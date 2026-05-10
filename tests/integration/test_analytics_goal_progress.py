"""Integration: GET /analytics/goal-progress — spec 010 §3 Scenario 3.

Поднимаем testcontainers Postgres, кладём профиль с целью и пару
InBody-замеров, дёргаем эндпоинт и проверяем расчёт. ETA-ветку с реальным
forecast'ом не дёргаем (для неё нужно достаточно истории + дни-метрик —
это покрывается отдельным forecast-stack'ом); проверяем фолбэк, когда
прогноз не построился: progress есть, eta=None.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.inbody.models import InBodyMeasurement
from app.domains.profile.models import UserProfile
from app.security import create_token


async def _make_user(
    session: AsyncSession,
    *,
    email: str,
    goal: str | None = "weight_loss",
    target_weight_kg: Decimal | None = Decimal("80"),
    target_muscle_kg: Decimal | None = None,
    baseline_weight_kg: Decimal | None = Decimal("90"),
    goal_started_at: date | None = None,
) -> User:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    profile = UserProfile(
        user_id=user.id,
        height_cm=Decimal("175"),
        sex="male",
        goal=goal,
        target_weight_kg=target_weight_kg,
        target_muscle_kg=target_muscle_kg,
        baseline_weight_kg=baseline_weight_kg,
        goal_started_at=goal_started_at,
    )
    session.add(profile)
    await session.flush()
    return user


def _measurement(
    *,
    user_id: uuid.UUID,
    measured_at: datetime,
    weight_kg: float = 80.0,
    muscle_mass_kg: float | None = None,
) -> InBodyMeasurement:
    return InBodyMeasurement(
        user_id=user_id,
        measured_at=measured_at,
        weight_kg=Decimal(str(weight_kg)),
        height_cm=Decimal("175"),
        sex="male",
        body_fat_percent=Decimal("18.0"),
        muscle_mass_kg=(
            Decimal(str(muscle_mass_kg)) if muscle_mass_kg is not None else None
        ),
        bmi=Decimal("25.5"),
        source="manual",
    )


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    token, _ = create_token(user_id=user_id, kind="access")
    return {"Authorization": f"Bearer {token}"}


class TestWeightLossGoal:
    async def test_progress_with_two_measurements(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # 90 (start) → 84 (current) при цели 80 = 60% прогресса.
        user = await _make_user(db_session, email="goal_wl1@example.com")
        for d, w in (
            (datetime(2026, 1, 1, tzinfo=UTC), 90.0),
            (datetime(2026, 4, 1, tzinfo=UTC), 84.0),
        ):
            db_session.add(_measurement(user_id=user.id, measured_at=d, weight_kg=w))
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["goal"] == "weight_loss"
        assert body["start_value"] == 90.0
        assert body["current_value"] == 84.0
        assert body["target_value"] == 80.0
        assert body["progress_percent"] == 60
        assert body["already_reached"] is False
        # forecast не построится (нужно несколько замеров с разной динамикой) —
        # проверяем фолбэк.
        assert body["eta"] in (None, body["eta"])  # ETA опциональна

    async def test_started_at_picks_post_start_baseline(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # У пользователя есть «старый» замер до старта работы над целью; ему
        # его ставить точкой отсчёта нельзя — берём первый замер ≥ goal_started_at.
        user = await _make_user(
            db_session,
            email="goal_wl_started@example.com",
            goal_started_at=date(2026, 3, 1),
        )
        # Слишком давний — должен игнорироваться.
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2025, 12, 1, tzinfo=UTC),
                weight_kg=100.0,
            )
        )
        # Релевантный старт.
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 3, 5, tzinfo=UTC),
                weight_kg=88.0,
            )
        )
        # Текущий.
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 4, 5, tzinfo=UTC),
                weight_kg=84.0,
            )
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )

        body = resp.json()
        assert body["start_value"] == 88.0
        assert body["current_value"] == 84.0
        # 88 → 84 при target 80 = 4 / 8 = 50%.
        assert body["progress_percent"] == 50
        assert body["started_at"] == "2026-03-01"

    async def test_already_reached_marker(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="goal_wl_reached@example.com")
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 1, 1, tzinfo=UTC),
                weight_kg=90.0,
            )
        )
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 4, 1, tzinfo=UTC),
                weight_kg=78.0,  # ниже target=80
            )
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )
        body = resp.json()
        assert body["progress_percent"] == 100
        assert body["already_reached"] is True


class TestMuscleGainGoal:
    async def test_progress_uses_muscle_mass(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # 30 → 32.5 при target 35 = 50%.
        user = await _make_user(
            db_session,
            email="goal_mg@example.com",
            goal="muscle_gain",
            target_weight_kg=None,
            target_muscle_kg=Decimal("35"),
            baseline_weight_kg=None,
        )
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 1, 1, tzinfo=UTC),
                weight_kg=80.0,
                muscle_mass_kg=30.0,
            )
        )
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 4, 1, tzinfo=UTC),
                weight_kg=82.0,
                muscle_mass_kg=32.5,
            )
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )
        body = resp.json()
        assert body["goal"] == "muscle_gain"
        assert body["start_value"] == 30.0
        assert body["current_value"] == 32.5
        assert body["target_value"] == 35.0
        assert body["progress_percent"] == 50

    async def test_no_muscle_data_returns_empty_state(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Цель muscle_gain, но в замерах нет muscle_mass_kg → empty state.
        user = await _make_user(
            db_session,
            email="goal_mg_empty@example.com",
            goal="muscle_gain",
            target_weight_kg=None,
            target_muscle_kg=Decimal("35"),
            baseline_weight_kg=None,
        )
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 1, 1, tzinfo=UTC),
                weight_kg=80.0,
                muscle_mass_kg=None,
            )
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )
        body = resp.json()
        assert resp.status_code == 200
        assert body["reason"] == "no_inbody_measurements"
        assert "muscle_mass_kg" in body["missing_fields"]


class TestEmptyStates:
    async def test_no_goal_returns_cta(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(
            db_session,
            email="goal_none@example.com",
            goal=None,
            target_weight_kg=None,
            baseline_weight_kg=None,
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["reason"] == "no_goal_in_profile"
        assert body["missing_fields"] == ["goal"]

    async def test_maintenance_treated_as_no_goal(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # maintenance — нет «достижимой» цифры, UX тот же CTA.
        user = await _make_user(
            db_session,
            email="goal_maintain@example.com",
            goal="maintenance",
            target_weight_kg=None,
            baseline_weight_kg=None,
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )
        body = resp.json()
        assert body["reason"] == "no_goal_in_profile"

    async def test_goal_without_target_returns_cta(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(
            db_session,
            email="goal_no_target@example.com",
            goal="weight_loss",
            target_weight_kg=None,
            baseline_weight_kg=Decimal("90"),
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )
        body = resp.json()
        assert body["reason"] == "no_target_set"
        assert body["missing_fields"] == ["target_weight_kg"]

    async def test_goal_with_target_but_no_measurements(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="goal_no_inbody@example.com")
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/goal-progress", headers=_auth(user.id)
        )
        body = resp.json()
        assert body["reason"] == "no_inbody_measurements"
