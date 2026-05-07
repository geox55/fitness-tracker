"""Сервис импорта PDF InBody — spec 013.

Минимальный flow для MVP — синхронный (REQ-01 говорит про async-flow,
но на маленьких PDF (≤2 MB) парсинг укладывается в 1-2 секунды;
voraussetzungen для асинхронного worker'а — отдельная задача когда поднимем
очередь). Текст извлекается pdfplumber'ом сразу в обработчике, парсер
из `app.domain.inbody_pdf` отвечает только за вытаскивание полей.

Хуки для spec 008/009 (forecast-evaluation + weight-watcher) запускаются
из `inbody.service.create_manual` через `confirm_import` → `create_manual`.
"""

from __future__ import annotations

import io
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import pdfplumber
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.inbody_pdf import (
    ParsedInBody,
    extract_fields,
    is_inbody,
)
from ...storage import Storage
from ..inbody.models import InBodyMeasurement
from ..inbody.service import create_manual as create_manual_measurement
from .models import JobStatus, PdfImportJob

_log = logging.getLogger("app.inbody_pdf")

MAX_PDF_BYTES = 10 * 1024 * 1024  # REQ-10
PDF_CONTENT_TYPE = "application/pdf"


class PdfImportError(Exception):
    code: str = "pdf_import_error"


class FileTooLargeError(PdfImportError):
    code = "file_too_large"


class JobNotFoundError(PdfImportError):
    code = "not_found"


class JobAlreadyConfirmedError(PdfImportError):
    code = "already_confirmed"


class JobNotReadyError(PdfImportError):
    code = "not_ready"


# ---------------------------------------------------------------------------
# Извлечение текста и определение статуса
# ---------------------------------------------------------------------------


def _extract_text_from_pdf(data: bytes) -> tuple[str, JobStatus | None]:
    """Возвращает (text, status_override).

    status_override — `'encrypted'` или `'scanned_unsupported'` если файл
    нельзя обработать. None — если текст успешно извлечён.
    """
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            if not pdf.pages:
                return "", "failed"
            # Берём первую страницу (REQ + Edge case §10: один PDF — один замер).
            text = pdf.pages[0].extract_text() or ""
    except Exception as exc:
        # pdfplumber кидает разные исключения; типичный случай — encrypted PDF.
        msg = str(exc).lower()
        if "encrypt" in msg or "password" in msg:
            return "", "encrypted"
        _log.exception("pdfplumber failed to open file")
        return "", "failed"

    if len(text.strip()) < 30:
        # Текстовый слой пустой — это скан без OCR.
        return "", "scanned_unsupported"
    return text, None


def _classify_status(parsed: ParsedInBody) -> JobStatus:
    """Решаем status по тому, что удалось вытащить.

    'ready' — есть и weight, и body_fat (минимум для последующего
    создания InBodyMeasurement). 'partial' — что-то нашлось, но
    не хватает обязательных. 'failed' — ничего не вытащили.
    """
    if "weight_kg" in parsed.extracted and "body_fat_percent" in parsed.extracted:
        return "ready"
    if parsed.extracted:
        return "partial"
    return "failed"


# ---------------------------------------------------------------------------
# Главный flow
# ---------------------------------------------------------------------------


def _temp_key(user_id: uuid.UUID, job_id: uuid.UUID) -> str:
    return f"inbody-pdf/temp/{user_id}/{job_id}.pdf"


async def start_import(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    file_bytes: bytes,
    storage: Storage,
) -> PdfImportJob:
    """REQ-10: лимит 10 MB. Превышение → 400 в API."""
    if len(file_bytes) > MAX_PDF_BYTES:
        raise FileTooLargeError(
            f"PDF size {len(file_bytes)} > limit {MAX_PDF_BYTES}"
        )

    text, status_override = _extract_text_from_pdf(file_bytes)

    parsed: ParsedInBody | None = None
    if status_override is None and not is_inbody(text):
        status: JobStatus = "not_inbody"
    elif status_override is not None:
        status = status_override
    else:
        parsed = extract_fields(text)
        status = _classify_status(parsed)

    job = PdfImportJob(
        id=uuid.uuid4(),
        user_id=user_id,
        status=status,
        template=parsed.template if parsed is not None else None,
        extracted=dict(parsed.extracted) if parsed is not None else {},
        confidence=dict(parsed.confidence) if parsed is not None else {},
        missing_fields=list(parsed.missing_fields) if parsed is not None else [],
        temp_pdf_key=_temp_key(user_id, uuid.uuid4()),  # placeholder, перезапишем
        error_message=None,
    )
    # Только если сам файл нам интересен (не not_inbody/encrypted/scanned/failed)
    # — сохраняем его в storage для последующего confirm.
    if status in ("ready", "partial"):
        job.temp_pdf_key = _temp_key(user_id, job.id)
        await storage.put(
            key=job.temp_pdf_key,
            data=file_bytes,
            content_type=PDF_CONTENT_TYPE,
        )
    else:
        # Для пустых статусов кладём ключ-маркер, что файла нет; БД-NOT NULL.
        job.temp_pdf_key = ""

    session.add(job)
    await session.flush()
    return job


async def get_job(
    session: AsyncSession, *, user_id: uuid.UUID, job_id: uuid.UUID
) -> PdfImportJob:
    stmt = select(PdfImportJob).where(
        PdfImportJob.id == job_id,
        PdfImportJob.user_id == user_id,
    )
    job = (await session.execute(stmt)).scalar_one_or_none()
    if job is None:
        raise JobNotFoundError(f"job {job_id} not found")
    return job


async def confirm_import(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
    overrides: dict[str, Any] | None = None,
    storage: Storage,
    measured_at: datetime | None = None,
    now: datetime | None = None,
) -> InBodyMeasurement:
    """Создать измерение InBody из распознанного Job + (опц.) правок UI.

    `overrides` — словарь поле→значение, которыми пользователь поправил
    распознанные значения на превью (Spec 013 §7 «Превью PDF»).

    После успеха job помечается `confirmed_at`. Сам файл остаётся в той же
    location storage (publish-after-confirm) — переноса между bucket'ами
    в MVP не делаем; cleanup неподтверждённых будет отдельным cron-job'ом.
    """
    now = now or datetime.now(UTC)
    job = await get_job(session, user_id=user_id, job_id=job_id)

    if job.confirmed_at is not None:
        raise JobAlreadyConfirmedError(f"job {job_id} already confirmed")
    if job.status not in ("ready", "partial"):
        raise JobNotReadyError(
            f"job status '{job.status}' cannot be confirmed"
        )

    payload: dict[str, Any] = {
        "measured_at": measured_at or now,
    }
    payload.update(job.extracted)
    if overrides:
        payload.update(overrides)

    if "weight_kg" not in payload or "body_fat_percent" not in payload:
        raise JobNotReadyError(
            "weight_kg and body_fat_percent are required to create measurement"
        )

    measurement = await create_manual_measurement(
        session, user_id=user_id, payload=payload
    )
    # Источник перепишем с 'manual' на 'pdf' и привяжем оригинал.
    measurement.source = "pdf"
    measurement.original_pdf_url = storage.public_url(job.temp_pdf_key)
    job.confirmed_at = now
    await session.flush()
    return measurement
