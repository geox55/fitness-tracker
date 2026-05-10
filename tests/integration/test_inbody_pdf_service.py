"""Integration: cleanup-job + stats-эндпоинт PDF-импорта (spec 013 §9, REQ-08/09).

Юниты не покрывают БД-orchestration `cleanup_expired_jobs` и
`template_stats` — здесь поднимаем настоящий Postgres через testcontainers
(см. `tests/integration/conftest.py`), создаём фикстурные job'ы и проверяем
поведение.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.inbody_pdf.models import PdfImportJob
from app.domains.inbody_pdf.service import (
    cleanup_expired_jobs,
    template_stats,
)
from app.security import create_token
from app.storage import InMemoryStorage


async def _make_user(session: AsyncSession, *, email: str) -> User:
    user = User(
        email=email,
        password_hash="x",  # хэш не проверяем в этих тестах
        email_status="active",
    )
    session.add(user)
    await session.flush()
    return user


def _job(
    *,
    user_id: uuid.UUID,
    created_at: datetime,
    confirmed_at: datetime | None = None,
    template: str | None = "inbody_770",
    status: str = "ready",
    temp_pdf_key: str = "",
) -> PdfImportJob:
    return PdfImportJob(
        id=uuid.uuid4(),
        user_id=user_id,
        status=status,
        template=template,
        extracted={"weight_kg": 80.0, "body_fat_percent": 18.0},
        confidence={"weight_kg": "high", "body_fat_percent": "high"},
        missing_fields=[],
        temp_pdf_key=temp_pdf_key,
        error_message=None,
        created_at=created_at,
        confirmed_at=confirmed_at,
    )


class TestCleanupExpiredJobs:
    async def test_removes_old_unconfirmed_and_keeps_fresh(
        self, db_session: AsyncSession
    ) -> None:
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        user = await _make_user(db_session, email="cleanup1@example.com")
        storage = InMemoryStorage()

        # Старая запись с файлом — должна исчезнуть.
        old = _job(
            user_id=user.id,
            created_at=now - timedelta(hours=2),
            temp_pdf_key="inbody-pdf/temp/old.pdf",
        )
        await storage.put(
            key=old.temp_pdf_key, data=b"%PDF-1.4 fake", content_type="application/pdf"
        )
        # Свежая запись (внутри TTL) — остаётся.
        fresh = _job(
            user_id=user.id,
            created_at=now - timedelta(minutes=5),
            temp_pdf_key="inbody-pdf/temp/fresh.pdf",
        )
        await storage.put(
            key=fresh.temp_pdf_key, data=b"%PDF-1.4 fake", content_type="application/pdf"
        )
        db_session.add_all([old, fresh])
        await db_session.flush()

        deleted = await cleanup_expired_jobs(
            db_session, storage=storage, now=now, ttl=timedelta(hours=1)
        )

        assert deleted == 1
        survivors = (
            await db_session.execute(
                select(PdfImportJob).where(PdfImportJob.user_id == user.id)
            )
        ).scalars().all()
        assert [j.id for j in survivors] == [fresh.id]
        assert storage.list_keys() == ["inbody-pdf/temp/fresh.pdf"]

    async def test_keeps_confirmed_even_if_old(
        self, db_session: AsyncSession
    ) -> None:
        # REQ-07: подтверждённый job — его файл уже принадлежит измерению,
        # cleanup не должен его трогать.
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        user = await _make_user(db_session, email="cleanup2@example.com")
        storage = InMemoryStorage()

        old_confirmed = _job(
            user_id=user.id,
            created_at=now - timedelta(days=3),
            confirmed_at=now - timedelta(days=3, hours=-1),
            temp_pdf_key="inbody-pdf/temp/kept.pdf",
        )
        await storage.put(
            key=old_confirmed.temp_pdf_key,
            data=b"%PDF-1.4 fake",
            content_type="application/pdf",
        )
        db_session.add(old_confirmed)
        await db_session.flush()

        deleted = await cleanup_expired_jobs(
            db_session, storage=storage, now=now, ttl=timedelta(hours=1)
        )

        assert deleted == 0
        assert storage.list_keys() == ["inbody-pdf/temp/kept.pdf"]

    async def test_zero_when_nothing_expired(
        self, db_session: AsyncSession
    ) -> None:
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        user = await _make_user(db_session, email="cleanup3@example.com")
        storage = InMemoryStorage()
        db_session.add(
            _job(user_id=user.id, created_at=now - timedelta(minutes=10))
        )
        await db_session.flush()

        deleted = await cleanup_expired_jobs(
            db_session, storage=storage, now=now, ttl=timedelta(hours=1)
        )

        assert deleted == 0

    async def test_missing_storage_key_is_ignored(
        self, db_session: AsyncSession
    ) -> None:
        # REQ-08: cleanup идемпотентен — отсутствие файла в storage
        # (например, S3 уже удалил его при предыдущем неудачном проходе)
        # не должен ломать удаление записи в БД.
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        user = await _make_user(db_session, email="cleanup4@example.com")
        storage = InMemoryStorage()

        orphan = _job(
            user_id=user.id,
            created_at=now - timedelta(hours=2),
            temp_pdf_key="inbody-pdf/temp/already-gone.pdf",
        )
        # Намеренно не кладём файл в storage.
        db_session.add(orphan)
        await db_session.flush()

        deleted = await cleanup_expired_jobs(
            db_session, storage=storage, now=now, ttl=timedelta(hours=1)
        )

        assert deleted == 1


class TestTemplateStats:
    async def test_counts_by_template_with_unknown_bucket(
        self, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="stats1@example.com")
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        rows: list[dict[str, Any]] = [
            # 3× inbody_770
            {"template": "inbody_770"},
            {"template": "inbody_770"},
            {"template": "inbody_770"},
            # 2× inbody_270
            {"template": "inbody_270"},
            {"template": "inbody_270"},
            # 1× generic
            {"template": "generic"},
            # 2× null (не InBody / не распознан)
            {"template": None, "status": "not_inbody"},
            {"template": None, "status": "encrypted"},
        ]
        for r in rows:
            db_session.add(
                _job(user_id=user.id, created_at=now, **r)
            )
        await db_session.flush()

        counts = await template_stats(db_session)

        assert counts["inbody_770"] == 3
        assert counts["inbody_270"] == 2
        assert counts["generic"] == 1
        assert counts["unknown"] == 2

    async def test_endpoint_returns_counts(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="stats-api@example.com")
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        db_session.add(_job(user_id=user.id, created_at=now, template="inbody_770"))
        db_session.add(_job(user_id=user.id, created_at=now, template="inbody_770"))
        db_session.add(_job(user_id=user.id, created_at=now, template="generic"))
        await db_session.commit()

        token, _ = create_token(user_id=user.id, kind="access")
        resp = await client.get(
            "/api/v1/internal/inbody-pdf/templates/stats",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["templates_recognized"]["inbody_770"] == 2
        assert body["templates_recognized"]["generic"] == 1

    async def test_endpoint_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/internal/inbody-pdf/templates/stats")
        assert resp.status_code == 401
