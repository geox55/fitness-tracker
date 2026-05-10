"""Сервис импорта PDF InBody — spec 013.

Минимальный flow для MVP — синхронный (REQ-01 говорит про async-flow,
но на маленьких PDF (≤2 MB) парсинг укладывается в 1-2 секунды;
voraussetzungen для асинхронного worker'а — отдельная задача, когда
поднимем очередь). Текст извлекается pdfplumber'ом сразу в обработчике,
вся не-БД-логика (что делать с этим текстом) уезжает в
`app.domain.inbody_pdf.planner`.

Хуки для spec 008/009 (forecast-evaluation + weight-watcher) запускаются
из `inbody.service.create_manual` через `confirm_import` → `create_manual`.
"""

from __future__ import annotations

import io
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pdfplumber
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.inbody_pdf import (
    ImportPlan,
    JobStatus,
    has_required_fields,
    merge_for_confirmation,
    plan_import,
)
from ...storage import Storage
from ..inbody.models import InBodyMeasurement
from ..inbody.service import create_manual as create_manual_measurement
from .models import PdfImportJob

_log = logging.getLogger("app.inbody_pdf")

MAX_PDF_BYTES = 10 * 1024 * 1024  # REQ-10
PDF_CONTENT_TYPE = "application/pdf"

# REQ-08: неподтверждённые job'ы и их temp-файлы удаляются через 1 час.
TEMP_TTL = timedelta(hours=1)


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
# Извлечение текста (тонкая обёртка над pdfplumber)
# ---------------------------------------------------------------------------


def _extract_text_from_pdf(data: bytes) -> tuple[str, JobStatus | None]:
    """Возвращает (text, status_override).

    status_override — `'encrypted'` / `'scanned_unsupported'` / `'failed'`,
    если файл нельзя обработать (передаётся в planner как готовый ответ).
    None — если текст успешно извлечён, planner решит дальше.
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


# ---------------------------------------------------------------------------
# Главный flow
# ---------------------------------------------------------------------------


def _temp_key(user_id: uuid.UUID, job_id: uuid.UUID) -> str:
    return f"inbody-pdf/temp/{user_id}/{job_id}.pdf"


def _build_job(
    *, user_id: uuid.UUID, job_id: uuid.UUID, plan: ImportPlan, temp_key: str
) -> PdfImportJob:
    """Собрать ORM-объект из плана. Не пишет в БД — это удобно для тестов."""
    parsed = plan.parsed
    return PdfImportJob(
        id=job_id,
        user_id=user_id,
        status=plan.status,
        template=parsed.template if parsed is not None else None,
        extracted=dict(parsed.extracted) if parsed is not None else {},
        confidence=dict(parsed.confidence) if parsed is not None else {},
        missing_fields=list(parsed.missing_fields) if parsed is not None else [],
        temp_pdf_key=temp_key,
        error_message=None,
    )


async def start_import(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    file_bytes: bytes,
    storage: Storage,
) -> PdfImportJob:
    """REQ-10: лимит 10 MB. Превышение → 413 в API."""
    if len(file_bytes) > MAX_PDF_BYTES:
        raise FileTooLargeError(
            f"PDF size {len(file_bytes)} > limit {MAX_PDF_BYTES}"
        )

    text, status_override = _extract_text_from_pdf(file_bytes)
    plan = plan_import(text=text, status_override=status_override)

    job_id = uuid.uuid4()
    # Если файл планируем оставить — кладём по нормальному ключу;
    # иначе пустая строка как маркер «нет файла» (БД-NOT NULL).
    temp_key = _temp_key(user_id, job_id) if plan.persist_file else ""

    if plan.persist_file:
        await storage.put(
            key=temp_key,
            data=file_bytes,
            content_type=PDF_CONTENT_TYPE,
        )

    job = _build_job(user_id=user_id, job_id=job_id, plan=plan, temp_key=temp_key)
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
    measured_at: datetime | None = None,
    now: datetime | None = None,
) -> InBodyMeasurement:
    """Создать измерение InBody из распознанного Job + (опц.) правок UI.

    После успеха job помечается `confirmed_at`. Сам файл остаётся в той же
    location storage (publish-after-confirm) — переноса между bucket'ами
    в MVP не делаем; cleanup неподтверждённых выполняет
    `cleanup_expired_jobs` (REQ-08). Storage сюда не нужен — мы пишем
    storage-key, а signed URL генерируется при сериализации в API.
    """
    now = now or datetime.now(UTC)
    job = await get_job(session, user_id=user_id, job_id=job_id)

    if job.confirmed_at is not None:
        raise JobAlreadyConfirmedError(f"job {job_id} already confirmed")
    if job.status not in ("ready", "partial"):
        raise JobNotReadyError(
            f"job status '{job.status}' cannot be confirmed"
        )

    payload = merge_for_confirmation(
        extracted=job.extracted,
        overrides=overrides,
        measured_at=measured_at or now,
    )
    if not has_required_fields(payload):
        raise JobNotReadyError(
            "weight_kg and body_fat_percent are required to create measurement"
        )

    measurement = await create_manual_measurement(
        session, user_id=user_id, payload=payload
    )
    # Источник перепишем с 'manual' на 'pdf' и привяжем оригинал.
    # Храним именно storage-key (а не public URL): доступ к файлу выдаётся
    # signed_url'ом из API на лету, чтобы PDF не был доступен по прямой
    # ссылке всем подряд (NFR-04 spec 013).
    measurement.source = "pdf"
    measurement.original_pdf_key = job.temp_pdf_key
    job.confirmed_at = now
    await session.flush()
    return measurement


# ---------------------------------------------------------------------------
# Cleanup неподтверждённых job'ов (REQ-08)
# ---------------------------------------------------------------------------


async def cleanup_expired_jobs(
    session: AsyncSession,
    *,
    storage: Storage,
    now: datetime | None = None,
    ttl: timedelta = TEMP_TTL,
) -> int:
    """Удалить job'ы старше TTL без `confirmed_at` + их temp-файлы из storage.

    Возвращает число удалённых записей. Идемпотентно: запуск без работы
    не падает. `now`/`ttl` параметризованы — удобно для тестов.
    """
    now = now or datetime.now(UTC)
    cutoff = now - ttl

    stmt = select(PdfImportJob).where(
        PdfImportJob.confirmed_at.is_(None),
        PdfImportJob.created_at < cutoff,
    )
    jobs = list((await session.execute(stmt)).scalars().all())
    if not jobs:
        return 0

    for job in jobs:
        if job.temp_pdf_key:
            # Storage-API идемпотентен по контракту; промахи не критичны,
            # но логируем — иначе будет тяжело найти осиротевший файл.
            try:
                await storage.delete(key=job.temp_pdf_key)
            except Exception:
                _log.exception(
                    "failed to delete temp pdf %s for job %s",
                    job.temp_pdf_key,
                    job.id,
                )

    ids = [job.id for job in jobs]
    await session.execute(
        delete(PdfImportJob).where(PdfImportJob.id.in_(ids))
    )
    await session.flush()
    _log.info("inbody_pdf cleanup: removed %d expired jobs", len(jobs))
    return len(jobs)


# ---------------------------------------------------------------------------
# Stats (REQ-09)
# ---------------------------------------------------------------------------


async def template_stats(session: AsyncSession) -> dict[str, int]:
    """Counter по template — сколько job'ов какого шаблона распознано.

    `null`-template (документ не похож на InBody, либо не распознали модель,
    но сам InBody) ложится в ключ `'unknown'` — соответствует §9 spec'и.
    `'generic'` остаётся отдельным бакетом (это InBody, но без known-модели).
    """
    stmt = select(PdfImportJob.template, func.count(PdfImportJob.id)).group_by(
        PdfImportJob.template
    )
    rows = (await session.execute(stmt)).all()
    counts: dict[str, int] = {}
    for template, count in rows:
        key = template if template is not None else "unknown"
        counts[key] = int(count)
    return counts
