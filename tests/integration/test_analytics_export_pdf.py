"""Integration: POST /analytics/export-pdf + GET /{job_id} — spec 010 REQ-10..12.

Async-flow проверяем через polling: после POST → 202 крутимся в GET до
status='ready' (≤ ~5с в e2e, fixture-storage InMemory почти мгновенный).
Также проверяем:
- 404 для чужого/несуществующего job;
- failed → error_message заполнен;
- range-валидацию;
- авторизацию.
"""

from __future__ import annotations

import asyncio
import io
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pdfplumber
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.inbody.models import InBodyMeasurement
from app.domains.profile.models import UserProfile
from app.domains.workouts.models import ExerciseLog, Workout
from app.security import create_token
from app.storage import InMemoryStorage, get_storage


async def _make_user(session: AsyncSession, *, email: str) -> User:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    return user


async def _make_profile(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    name: str = "Test User",
    goal: str | None = None,
    target_weight_kg: float | None = None,
) -> UserProfile:
    profile = UserProfile(
        user_id=user_id,
        name=name,
        sex="female",
        height_cm=Decimal("170.0"),
        goal=goal,
        target_weight_kg=(
            Decimal(str(target_weight_kg))
            if target_weight_kg is not None
            else None
        ),
    )
    session.add(profile)
    await session.flush()
    return profile


async def _make_measurement(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    measured_at: datetime,
    weight_kg: float,
    body_fat_percent: float | None = None,
    muscle_mass_kg: float | None = None,
) -> InBodyMeasurement:
    # body_fat_percent и bmi — NOT NULL в схеме (см. models). Если в тесте
    # body_fat_percent не задан, подставим 20.0 как «нормальный»; bmi считаем
    # из весоты/роста, чтобы CHECK BMI BETWEEN 5 AND 70 точно прошёл.
    bf = body_fat_percent if body_fat_percent is not None else 20.0
    bmi = round(weight_kg / ((170 / 100) ** 2), 1)
    m = InBodyMeasurement(
        user_id=user_id,
        measured_at=measured_at,
        source="manual",
        weight_kg=Decimal(str(weight_kg)),
        height_cm=Decimal("170.0"),
        sex="female",
        body_fat_percent=Decimal(str(bf)),
        muscle_mass_kg=(
            Decimal(str(muscle_mass_kg)) if muscle_mass_kg is not None else None
        ),
        bmi=Decimal(str(bmi)),
    )
    session.add(m)
    await session.flush()
    return m


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    token, _ = create_token(user_id=user_id, kind="access")
    return {"Authorization": f"Bearer {token}"}


async def _poll_status(
    client: AsyncClient,
    *,
    job_id: uuid.UUID,
    user_id: uuid.UUID,
    timeout_s: float = 5.0,
) -> dict[str, object]:
    """Дёргаем GET до status in ('ready','failed') или timeout."""
    deadline = asyncio.get_event_loop().time() + timeout_s
    last: dict[str, object] = {}
    while asyncio.get_event_loop().time() < deadline:
        resp = await client.get(
            f"/api/v1/analytics/export-pdf/{job_id}", headers=_auth(user_id)
        )
        assert resp.status_code == 200
        last = resp.json()
        if last.get("status") in ("ready", "failed"):
            return last
        await asyncio.sleep(0.05)
    raise AssertionError(f"job stayed in {last.get('status')!r} until timeout")


class TestExportPdfFlow:
    async def test_post_returns_202_with_job_id(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ep-post@example.com")
        await _make_profile(db_session, user_id=user.id)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/analytics/export-pdf",
            headers=_auth(user.id),
            json={"sections": ["profile"]},
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        # Только что созданный job — pending или сразу running (если фон уже стартовал).
        assert body["status"] in ("pending", "running", "ready")

    async def test_full_flow_to_ready(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Полный цикл: пользователь с профилем и InBody, экспорт всех секций.
        # PDF в InMemoryStorage просто bytes; signed_url работает на in-memory.
        user = await _make_user(db_session, email="ep-flow@example.com")
        await _make_profile(
            db_session,
            user_id=user.id,
            goal="weight_loss",
            target_weight_kg=68.0,
        )
        await _make_measurement(
            db_session,
            user_id=user.id,
            measured_at=datetime(2026, 1, 15, 10, 0, tzinfo=UTC),
            weight_kg=82.0,
            body_fat_percent=24.0,
            muscle_mass_kg=30.0,
        )
        await db_session.commit()

        resp = await client.post(
            "/api/v1/analytics/export-pdf",
            headers=_auth(user.id),
            json={},
        )
        assert resp.status_code == 202
        job_id = uuid.UUID(resp.json()["job_id"])

        final = await _poll_status(client, job_id=job_id, user_id=user.id)
        assert final["status"] == "ready", final
        assert final["url"] is not None
        assert final["expires_at"] is not None
        # Эхо параметров запроса для UI.
        assert set(final["sections"]) == {  # type: ignore[arg-type]
            "profile",
            "inbody",
            "workouts",
            "goal",
        }

        # Скачиваем PDF из InMemoryStorage напрямую (signed_url на memory
        # хранилище не возвращает реальный HTTP), достаточно убедиться, что
        # storage.put прошёл — проверим через приватный _objects.
        storage = get_storage()
        assert isinstance(storage, InMemoryStorage)
        # InMemoryStorage — singleton через @lru_cache (см. get_storage),
        # объекты прошлых тестов в нём остаются. Фильтруем по своему user_id.
        prefix = f"exports/{user.id}/"
        keys = [
            k for k in storage._objects  # type: ignore[attr-defined]
            if k.startswith(prefix) and k.endswith(".pdf")
        ]
        assert len(keys) == 1
        pdf_bytes, _ct = storage._objects[keys[0]]  # type: ignore[attr-defined]
        assert pdf_bytes.startswith(b"%PDF-")
        # Содержит данные пользователя: имя и измерение.
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as doc:
            text = "\n".join((p.extract_text() or "") for p in doc.pages)
        assert "Test User" in text or "User" in text
        assert "82" in text  # weight_kg

    async def test_subset_sections_only_renders_them(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Запрос только profile — в PDF должны быть только профильные данные,
        # «InBody Measurements» отсутствуют.
        user = await _make_user(db_session, email="ep-subset@example.com")
        await _make_profile(db_session, user_id=user.id, name="Alice")
        await _make_measurement(
            db_session,
            user_id=user.id,
            measured_at=datetime(2026, 1, 15, 10, 0, tzinfo=UTC),
            weight_kg=82.0,
        )
        await db_session.commit()

        resp = await client.post(
            "/api/v1/analytics/export-pdf",
            headers=_auth(user.id),
            json={"sections": ["profile"]},
        )
        job_id = uuid.UUID(resp.json()["job_id"])
        final = await _poll_status(client, job_id=job_id, user_id=user.id)
        assert final["status"] == "ready"
        assert final["sections"] == ["profile"]

        storage = get_storage()
        assert isinstance(storage, InMemoryStorage)
        prefix = f"exports/{user.id}/"
        keys = [
            k for k in storage._objects  # type: ignore[attr-defined]
            if k.startswith(prefix) and k.endswith(".pdf")
        ]
        pdf_bytes, _ct = storage._objects[keys[-1]]  # type: ignore[attr-defined]
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as doc:
            text = "\n".join((p.extract_text() or "") for p in doc.pages)
        assert "Alice" in text
        assert "InBody Measurements" not in text

    async def test_inverted_range_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ep-range@example.com")
        await db_session.commit()
        resp = await client.post(
            "/api/v1/analytics/export-pdf",
            headers=_auth(user.id),
            json={"from": "2026-03-01", "to": "2026-02-01"},
        )
        assert resp.status_code == 400
        assert resp.json()["detail"]["error"] == "invalid_range"

    async def test_unknown_job_404(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ep-404@example.com")
        await db_session.commit()
        resp = await client.get(
            f"/api/v1/analytics/export-pdf/{uuid.uuid4()}",
            headers=_auth(user.id),
        )
        assert resp.status_code == 404
        assert resp.json()["detail"]["error"] == "job_not_found"

    async def test_other_users_job_is_404(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Изоляция: Alice не должна увидеть job Bob'а даже зная его UUID.
        alice = await _make_user(db_session, email="ep-alice@example.com")
        bob = await _make_user(db_session, email="ep-bob@example.com")
        await _make_profile(db_session, user_id=bob.id)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/analytics/export-pdf",
            headers=_auth(bob.id),
            json={},
        )
        bob_job_id = resp.json()["job_id"]

        resp = await client.get(
            f"/api/v1/analytics/export-pdf/{bob_job_id}",
            headers=_auth(alice.id),
        )
        assert resp.status_code == 404

    async def test_unknown_section_in_request_is_ignored(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Forward compat: незнакомая секция в JSON не валит запрос (400),
        # а просто отфильтровывается. Это важно при разъезде API/UI версий.
        user = await _make_user(db_session, email="ep-unknown@example.com")
        await _make_profile(db_session, user_id=user.id)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/analytics/export-pdf",
            headers=_auth(user.id),
            json={"sections": ["profile", "made_up_section"]},
        )
        assert resp.status_code == 202
        job_id = uuid.UUID(resp.json()["job_id"])
        final = await _poll_status(client, job_id=job_id, user_id=user.id)
        assert final["sections"] == ["profile"]

    async def test_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/analytics/export-pdf", json={})
        assert resp.status_code == 401

        resp = await client.get(
            f"/api/v1/analytics/export-pdf/{uuid.uuid4()}"
        )
        assert resp.status_code == 401


class TestExportPdfFailureHandling:
    async def test_failure_reports_error_message(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Симулируем падение в storage.put → status=failed, error_message заполнен.
        from app.storage import InMemoryStorage

        async def _boom(self: InMemoryStorage, **_: object) -> str:
            raise RuntimeError("boom")

        monkeypatch.setattr(InMemoryStorage, "put", _boom, raising=True)

        user = await _make_user(db_session, email="ep-fail@example.com")
        await _make_profile(db_session, user_id=user.id)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/analytics/export-pdf",
            headers=_auth(user.id),
            json={"sections": ["profile"]},
        )
        job_id = uuid.UUID(resp.json()["job_id"])
        final = await _poll_status(client, job_id=job_id, user_id=user.id)
        assert final["status"] == "failed", final
        assert final["error_message"] is not None
        assert "RuntimeError" in final["error_message"]  # type: ignore[operator]
        assert final["url"] is None
