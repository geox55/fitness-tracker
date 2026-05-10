"""Integration: GET /analytics/inbody (серия) + /analytics/inbody/compare
— spec 010 §9.

Поднимаем testcontainers Postgres, делаем несколько InBodyMeasurement
напрямую через ORM (минуя API) и дёргаем эндпоинты через AsyncClient.
Forecast не строим — это покрывается отдельными тестами forecast'а.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.inbody.models import InBodyMeasurement
from app.domains.profile.models import UserProfile
from app.security import create_token


async def _make_user(session: AsyncSession, *, email: str) -> User:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    profile = UserProfile(
        user_id=user.id,
        height_cm=Decimal("175"),
        sex="male",
    )
    session.add(profile)
    await session.flush()
    return user


def _measurement(
    *,
    user_id: uuid.UUID,
    measured_at: datetime,
    weight_kg: float = 80.0,
    body_fat_percent: float = 18.0,
    muscle_mass_kg: float | None = None,
) -> InBodyMeasurement:
    return InBodyMeasurement(
        user_id=user_id,
        measured_at=measured_at,
        weight_kg=Decimal(str(weight_kg)),
        height_cm=Decimal("175"),
        sex="male",
        body_fat_percent=Decimal(str(body_fat_percent)),
        muscle_mass_kg=(
            Decimal(str(muscle_mass_kg))
            if muscle_mass_kg is not None
            else None
        ),
        bmi=Decimal("25.5"),
        source="manual",
    )


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    token, _ = create_token(user_id=user_id, kind="access")
    return {"Authorization": f"Bearer {token}"}


class TestInBodySeries:
    async def test_returns_history_in_order(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="series1@example.com")
        # Намеренно вставляем не по порядку — сервис должен сам отсортировать.
        for d, w in (
            (datetime(2026, 3, 1, tzinfo=UTC), 82.0),
            (datetime(2026, 1, 15, tzinfo=UTC), 84.0),
            (datetime(2026, 2, 15, tzinfo=UTC), 83.0),
        ):
            db_session.add(_measurement(user_id=user.id, measured_at=d, weight_kg=w))
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=weight_kg&forecast=false",
            headers=_auth(user.id),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["metric"] == "weight_kg"
        assert [p["value"] for p in body["points"]] == [84.0, 83.0, 82.0]
        assert [p["date"] for p in body["points"]] == [
            "2026-01-15",
            "2026-02-15",
            "2026-03-01",
        ]
        # forecast=false → блок прогноза отсутствует.
        assert body["forecast"] is None

    async def test_filters_by_from_to_inclusively(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # `to=YYYY-MM-DD` должно ВКЛЮЧАТЬ записи этого дня (inclusive end).
        user = await _make_user(db_session, email="series2@example.com")
        for d, w in (
            (datetime(2026, 1, 10, tzinfo=UTC), 84.0),  # вне диапазона (раньше from)
            (datetime(2026, 2, 1, 10, 0, tzinfo=UTC), 83.0),  # внутри
            (datetime(2026, 2, 28, 23, 0, tzinfo=UTC), 82.0),  # внутри (последний день)
            (datetime(2026, 3, 1, tzinfo=UTC), 81.0),   # вне (после to)
        ):
            db_session.add(_measurement(user_id=user.id, measured_at=d, weight_kg=w))
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=weight_kg"
            "&from=2026-02-01&to=2026-02-28&forecast=false",
            headers=_auth(user.id),
        )

        assert resp.status_code == 200
        values = [p["value"] for p in resp.json()["points"]]
        assert values == [83.0, 82.0]

    async def test_skips_measurements_without_metric(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Если у замера нет muscle_mass_kg — не показываем «дырку» в графике
        # (точка пропускается).
        user = await _make_user(db_session, email="series3@example.com")
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 1, 1, tzinfo=UTC),
                muscle_mass_kg=35.0,
            )
        )
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 1, 15, tzinfo=UTC),
                muscle_mass_kg=None,
            )
        )
        db_session.add(
            _measurement(
                user_id=user.id,
                measured_at=datetime(2026, 2, 1, tzinfo=UTC),
                muscle_mass_kg=36.0,
            )
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=muscle_mass_kg&forecast=false",
            headers=_auth(user.id),
        )

        body = resp.json()
        assert [p["value"] for p in body["points"]] == [35.0, 36.0]

    async def test_invalid_metric_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="series-err@example.com")
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=fake_field",
            headers=_auth(user.id),
        )

        assert resp.status_code == 400
        assert resp.json()["detail"]["error"] == "invalid_metric"

    async def test_inverted_range_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="series-bad-range@example.com")
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=weight_kg"
            "&from=2026-03-01&to=2026-02-01",
            headers=_auth(user.id),
        )

        assert resp.status_code == 400
        assert resp.json()["detail"]["error"] == "invalid_range"

    async def test_empty_history_returns_empty_points(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="series-empty@example.com")
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=weight_kg&forecast=false",
            headers=_auth(user.id),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["points"] == []
        assert body["forecast"] is None

    async def test_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/analytics/inbody?metric=weight_kg")
        assert resp.status_code == 401


class TestInBodyCompare:
    async def test_compare_returns_deltas(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="cmp1@example.com")
        a = _measurement(
            user_id=user.id,
            measured_at=datetime(2026, 1, 15, tzinfo=UTC),
            weight_kg=82.0,
            body_fat_percent=20.0,
            muscle_mass_kg=35.0,
        )
        b = _measurement(
            user_id=user.id,
            measured_at=datetime(2026, 2, 15, tzinfo=UTC),
            weight_kg=80.0,
            body_fat_percent=18.0,
            muscle_mass_kg=36.0,
        )
        db_session.add_all([a, b])
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/inbody/compare?a={a.id}&b={b.id}",
            headers=_auth(user.id),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["a"]["id"] == str(a.id)
        assert body["b"]["id"] == str(b.id)

        deltas = {d["field"]: d for d in body["deltas"]}
        assert deltas["weight_kg"]["delta_absolute"] == -2.0
        assert deltas["body_fat_percent"]["delta_absolute"] == -2.0
        assert deltas["muscle_mass_kg"]["delta_absolute"] == 1.0

    async def test_compare_handles_missing_field_in_one_side(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="cmp2@example.com")
        a = _measurement(
            user_id=user.id,
            measured_at=datetime(2026, 1, 1, tzinfo=UTC),
            muscle_mass_kg=None,
        )
        b = _measurement(
            user_id=user.id,
            measured_at=datetime(2026, 2, 1, tzinfo=UTC),
            muscle_mass_kg=36.0,
        )
        db_session.add_all([a, b])
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/inbody/compare?a={a.id}&b={b.id}",
            headers=_auth(user.id),
        )

        body = resp.json()
        deltas = {d["field"]: d for d in body["deltas"]}
        # Поле есть только в b — delta_absolute должен быть None.
        assert deltas["muscle_mass_kg"]["value_a"] is None
        assert deltas["muscle_mass_kg"]["value_b"] == 36.0
        assert deltas["muscle_mass_kg"]["delta_absolute"] is None

    async def test_same_uuid_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="cmp-same@example.com")
        m = _measurement(
            user_id=user.id,
            measured_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        db_session.add(m)
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/inbody/compare?a={m.id}&b={m.id}",
            headers=_auth(user.id),
        )

        assert resp.status_code == 400
        assert resp.json()["detail"]["error"] == "same_measurement"

    async def test_other_users_measurement_404(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Если b принадлежит другому пользователю — 404, не утечь сам факт
        # существования замера.
        alice = await _make_user(db_session, email="cmp-alice@example.com")
        bob = await _make_user(db_session, email="cmp-bob@example.com")
        a = _measurement(
            user_id=alice.id, measured_at=datetime(2026, 1, 1, tzinfo=UTC)
        )
        bob_m = _measurement(
            user_id=bob.id, measured_at=datetime(2026, 1, 1, tzinfo=UTC)
        )
        db_session.add_all([a, bob_m])
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/inbody/compare?a={a.id}&b={bob_m.id}",
            headers=_auth(alice.id),
        )

        assert resp.status_code == 404
        assert resp.json()["detail"]["error"] == "measurement_not_found"

    async def test_unknown_uuid_404(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="cmp-404@example.com")
        m = _measurement(
            user_id=user.id, measured_at=datetime(2026, 1, 1, tzinfo=UTC)
        )
        db_session.add(m)
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/inbody/compare?a={m.id}&b={uuid.uuid4()}",
            headers=_auth(user.id),
        )

        assert resp.status_code == 404


class TestInBodySeriesWithForecast:
    """Smoke-test forecast-overlay'я: после ≥2 замеров spec 008 строит
    прогноз, и /analytics/inbody подмешивает его в response."""

    async def test_forecast_block_appears_for_forecastable_metric(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="fs1@example.com")
        base = datetime(2026, 1, 1, tzinfo=UTC)
        for i in range(4):
            db_session.add(
                _measurement(
                    user_id=user.id,
                    measured_at=base + timedelta(weeks=i),
                    weight_kg=82.0 - i * 0.5,
                    body_fat_percent=20.0 - i * 0.2,
                    muscle_mass_kg=35.0 + i * 0.1,
                )
            )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=weight_kg&forecast=true",
            headers=_auth(user.id),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["forecast"] is not None
        assert len(body["forecast"]["points"]) > 0
        first = body["forecast"]["points"][0]
        assert {"date", "value", "ci_low", "ci_high"} <= set(first)

    async def test_forecast_omitted_for_non_forecastable_metric(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # bmi не forecastable — пунктир не строим даже при forecast=true.
        user = await _make_user(db_session, email="fs2@example.com")
        base = datetime(2026, 1, 1, tzinfo=UTC)
        for i in range(4):
            db_session.add(
                _measurement(
                    user_id=user.id,
                    measured_at=base + timedelta(weeks=i),
                )
            )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/analytics/inbody?metric=bmi&forecast=true",
            headers=_auth(user.id),
        )

        body = resp.json()
        assert body["forecast"] is None
