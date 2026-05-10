"""Integration: confirm PDF → measurement.original_pdf_url приходит как
signed URL, а не как public URL (NFR-04 spec 013).

Поднимаем testcontainers Postgres + InMemoryStorage; делаем confirm через
сервис, читаем измерение через GET /inbody/measurements/{id}, проверяем
что URL содержит подпись и отличается от public_url(key).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.inbody.models import InBodyMeasurement
from app.domains.inbody_pdf.models import PdfImportJob
from app.domains.inbody_pdf.service import confirm_import
from app.domains.profile.models import UserProfile
from app.security import create_token
from app.storage import InMemoryStorage, get_storage


async def _make_user_with_profile(
    session: AsyncSession, *, email: str
) -> User:
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


def _ready_job(
    *,
    user_id: uuid.UUID,
    temp_pdf_key: str,
    created_at: datetime,
) -> PdfImportJob:
    return PdfImportJob(
        id=uuid.uuid4(),
        user_id=user_id,
        status="ready",
        template="inbody_770",
        extracted={"weight_kg": 78.0, "body_fat_percent": 18.0},
        confidence={"weight_kg": "high", "body_fat_percent": "high"},
        missing_fields=[],
        temp_pdf_key=temp_pdf_key,
        error_message=None,
        created_at=created_at,
    )


class TestSignedUrlOnConfirm:
    async def test_confirm_writes_storage_key_not_url(
        self, db_session: AsyncSession
    ) -> None:
        # Storage сюда не нужен confirm'у (мы пишем только key); проверяем
        # ровно это: после confirm в БД хранится temp_pdf_key, а не URL.
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        user = await _make_user_with_profile(db_session, email="signed1@example.com")
        job = _ready_job(
            user_id=user.id,
            temp_pdf_key="inbody-pdf/temp/abc.pdf",
            created_at=now - timedelta(minutes=5),
        )
        db_session.add(job)
        await db_session.flush()

        measurement = await confirm_import(
            db_session, user_id=user.id, job_id=job.id, now=now
        )

        assert measurement.source == "pdf"
        # В БД лежит ровно key — без http://, без подписи.
        assert measurement.original_pdf_key == "inbody-pdf/temp/abc.pdf"


class TestSignedUrlOnRead:
    async def test_get_measurement_returns_signed_url(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Подменяем фабрику storage на InMemory с известным public_base —
        # signed URL будет начинаться с него и содержать sig=/expires=.
        custom = InMemoryStorage(public_base="http://memory-storage")
        get_storage.cache_clear()

        try:
            from app import storage as storage_mod

            original_factory = storage_mod.get_storage
            storage_mod.get_storage = lambda: custom  # type: ignore[assignment]

            now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
            user = await _make_user_with_profile(
                db_session, email="signed2@example.com"
            )
            measurement = InBodyMeasurement(
                user_id=user.id,
                measured_at=now,
                weight_kg=Decimal("78.0"),
                height_cm=Decimal("175.0"),
                sex="male",
                body_fat_percent=Decimal("18.0"),
                bmi=Decimal("25.5"),
                source="pdf",
                original_pdf_key="inbody-pdf/temp/xyz.pdf",
            )
            db_session.add(measurement)
            await db_session.commit()

            token, _ = create_token(user_id=user.id, kind="access")
            resp = await client.get(
                f"/api/v1/inbody/measurements/{measurement.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert resp.status_code == 200
            url = resp.json()["original_pdf_url"]
            assert url is not None
            # Должна быть подпись и expiry — формы public_url ему не хватит.
            assert "sig=" in url
            assert "expires=" in url
            # И сам ключ должен присутствовать в URL.
            assert "inbody-pdf/temp/xyz.pdf" in url
            # Не должно быть голого public_url'а без подписи.
            assert url != custom.public_url("inbody-pdf/temp/xyz.pdf")
        finally:
            storage_mod.get_storage = original_factory  # type: ignore[assignment]
            get_storage.cache_clear()

    async def test_manual_measurement_has_no_pdf_url(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Ручной ввод не имеет original_pdf_key → response.original_pdf_url
        # должен быть null, никаких подписей не генерируем.
        now = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
        user = await _make_user_with_profile(db_session, email="signed3@example.com")
        measurement = InBodyMeasurement(
            user_id=user.id,
            measured_at=now,
            weight_kg=Decimal("78.0"),
            height_cm=Decimal("175.0"),
            sex="male",
            body_fat_percent=Decimal("18.0"),
            bmi=Decimal("25.5"),
            source="manual",
            original_pdf_key=None,
        )
        db_session.add(measurement)
        await db_session.commit()

        token, _ = create_token(user_id=user.id, kind="access")
        resp = await client.get(
            f"/api/v1/inbody/measurements/{measurement.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        assert resp.json()["original_pdf_url"] is None
