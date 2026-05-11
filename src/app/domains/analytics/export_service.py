"""Сервис экспорта PDF-отчёта — spec 010 REQ-10..12.

Async-flow: POST создаёт `PdfExportJob(status='pending')`, фоновая
корутина `process_export_job` собирает данные, рисует PDF и кладёт
в storage, обновляя `status` на `ready`/`failed`. GET по job_id
отдаёт статус и подписанный URL (TTL 1ч из NFR-03).

Дизайн-решения:

- BackgroundTasks (in-process), а не очередь — спека только что описала
  job_id+poll контракт, а реализация может быть любой; вытаскивать
  Redis/celery в проект ради одной фичи бессмысленно. NFR-02 (≤15с)
  укладывается в синхронный рендер.
- Background-функция сама открывает свою AsyncSession (через
  `_get_sessionmaker`) — DI Depends в BackgroundTasks не работает.
- Сборка данных делегирует уже существующим сервисам аналитики
  (`series`, `workouts_buckets`, `get_goal_progress`) — single source of
  truth, нет копипасты SQL.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, date, datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...domain.analytics.pdf_report import (
    GoalProgressSection,
    InBodySeriesSection,
    ProfileSection,
    ReportData,
    WorkoutsSection,
    build_pdf,
)
from ...storage import Storage
from ..profile.models import UserProfile
from .export_models import PdfExportJob
from .goal_service import GoalProgress, get_goal_progress
from .inbody_service import (
    series,
    to_datetime_inclusive_end,
    to_datetime_inclusive_start,
)
from .workouts_service import workouts_buckets

_log = logging.getLogger("app.analytics.export")

# REQ-10 / NFR-03 spec 010: PDF доступен только владельцу через signed URL,
# TTL = 1 час.
SIGNED_URL_TTL_SECONDS = 60 * 60

# Какие секции пользователь может включить в отчёт. Незнакомые секции в
# запросе нормализуются «отбрасыванием»: лишний noise лучше 4xx, т.к.
# UI и backend могут версионироваться по-разному.
SectionKey = Literal["profile", "inbody", "workouts", "goal"]
SUPPORTED_SECTIONS: tuple[str, ...] = ("profile", "inbody", "workouts", "goal")


class ExportError(Exception):
    code: str = "export_error"


class ExportJobNotFoundError(ExportError):
    code = "job_not_found"


# ---------------------------------------------------------------------------
# Старт job
# ---------------------------------------------------------------------------


def normalize_sections(raw: list[str] | None) -> list[str]:
    """Отсеять незнакомые секции и дедупнуть, сохраняя порядок."""
    if not raw:
        return list(SUPPORTED_SECTIONS)
    seen: set[str] = set()
    out: list[str] = []
    for s in raw:
        if s in SUPPORTED_SECTIONS and s not in seen:
            seen.add(s)
            out.append(s)
    return out or list(SUPPORTED_SECTIONS)


async def start_export_job(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    sections: list[str],
    period_from: datetime | None,
    period_to: datetime | None,
) -> PdfExportJob:
    """Создать row 'pending' и вернуть её ID. Запуск воркера — снаружи."""
    job = PdfExportJob(
        user_id=user_id,
        status="pending",
        sections=sections,
        period_from=period_from.date() if period_from is not None else None,
        period_to=period_to.date() if period_to is not None else None,
    )
    session.add(job)
    await session.flush()
    await session.refresh(job)
    return job


# ---------------------------------------------------------------------------
# Воркер
# ---------------------------------------------------------------------------


async def _load_profile(
    session: AsyncSession, *, user_id: uuid.UUID
) -> ProfileSection | None:
    profile = await session.get(UserProfile, user_id)
    if profile is None:
        return None
    age: int | None = None
    if profile.birth_date is not None:
        today = datetime.now(UTC).date()
        age = today.year - profile.birth_date.year - (
            (today.month, today.day)
            < (profile.birth_date.month, profile.birth_date.day)
        )
    return ProfileSection(
        display_name=profile.name or "User",
        sex=profile.sex,
        age=age,
        height_cm=float(profile.height_cm) if profile.height_cm is not None else None,
        goal=profile.goal,
        target_weight_kg=(
            float(profile.target_weight_kg)
            if profile.target_weight_kg is not None
            else None
        ),
        target_muscle_kg=(
            float(profile.target_muscle_kg)
            if profile.target_muscle_kg is not None
            else None
        ),
    )


async def _load_inbody(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    period_from: datetime | None,
    period_to: datetime | None,
) -> InBodySeriesSection:
    """Вытащить три ключевые метрики (REQ-11) одним вызовом per metric.

    `series` возвращает list[tuple[date, float]] — это ровно то, что
    ожидает InBodySeriesSection; передаём напрямую без преобразований.
    """
    async def _series(metric: str) -> list[tuple[date, float]]:
        history, _ = await series(
            session,
            user_id=user_id,
            metric=metric,
            from_=period_from,
            to=period_to,
            include_forecast=False,
        )
        return history

    weight = await _series("weight_kg")
    fat = await _series("body_fat_percent")
    muscle = await _series("muscle_mass_kg")
    return InBodySeriesSection(
        weight=weight,
        body_fat_percent=fat,
        muscle_mass_kg=muscle,
    )


async def _load_workouts(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    period_from: datetime | None,
    period_to: datetime | None,
) -> WorkoutsSection:
    rows = await workouts_buckets(
        session,
        user_id=user_id,
        bucket="week",
        from_=period_from,
        to=period_to,
    )
    return WorkoutsSection(bucket="week", items=rows)


async def _load_goal(
    session: AsyncSession, *, user_id: uuid.UUID
) -> GoalProgressSection | None:
    result = await get_goal_progress(session, user_id=user_id)
    if not isinstance(result, GoalProgress):
        return None
    return GoalProgressSection(
        goal=result.goal,
        start_value=result.start_value,
        current_value=result.current_value,
        target_value=result.target_value,
        progress_percent=result.progress_percent,
        eta=result.eta,
    )


async def _assemble_report(
    session: AsyncSession, *, job: PdfExportJob
) -> ReportData:
    """Собрать всё, что нужно для build_pdf, опираясь на выбранные секции."""
    period_from = (
        to_datetime_inclusive_start(job.period_from)
        if job.period_from is not None
        else None
    )
    period_to = (
        to_datetime_inclusive_end(job.period_to)
        if job.period_to is not None
        else None
    )

    selected = set(job.sections)
    profile = (
        await _load_profile(session, user_id=job.user_id)
        if "profile" in selected
        else None
    )
    inbody = (
        await _load_inbody(
            session,
            user_id=job.user_id,
            period_from=period_from,
            period_to=period_to,
        )
        if "inbody" in selected
        else None
    )
    workouts = (
        await _load_workouts(
            session,
            user_id=job.user_id,
            period_from=period_from,
            period_to=period_to,
        )
        if "workouts" in selected
        else None
    )
    goal = (
        await _load_goal(session, user_id=job.user_id)
        if "goal" in selected
        else None
    )

    return ReportData(
        generated_at=datetime.now(UTC).date(),
        period_from=job.period_from,
        period_to=job.period_to,
        profile=profile,
        inbody=inbody,
        workouts=workouts,
        goal=goal,
    )


def _storage_key(*, user_id: uuid.UUID, job_id: uuid.UUID) -> str:
    """Сегментация по user_id — никаких глобальных коллизий и удобно
    чистить ключи при удалении пользователя.
    """
    return f"exports/{user_id}/{job_id}.pdf"


async def process_export_job(
    *,
    job_id: uuid.UUID,
    sessionmaker: async_sessionmaker[AsyncSession],
    storage: Storage,
) -> None:
    """Фоновая обработка одного job: данные → PDF → storage → status=ready.

    Все исключения логируются и сохраняются в `error_message`; status
    становится `failed`. UI поймёт по status и покажет retry.

    Используется свой sessionmaker (не передаём сессию из request),
    потому что BackgroundTask переживёт запрос-сессию: к моменту
    выполнения исходная транзакция уже закоммитится и закроется.
    """
    async with sessionmaker() as session:
        job = await session.get(PdfExportJob, job_id)
        if job is None:
            _log.warning("export_job %s disappeared before processing", job_id)
            return
        if job.status not in ("pending", "failed"):
            # Повторная обработка готового/уже запущенного — defensive no-op.
            return

        job.status = "running"
        await session.commit()

        try:
            data = await _assemble_report(session, job=job)
            pdf_bytes = build_pdf(data)
            key = _storage_key(user_id=job.user_id, job_id=job.id)
            await storage.put(
                key=key, data=pdf_bytes, content_type="application/pdf"
            )

            job.pdf_key = key
            job.status = "ready"
            job.ready_at = datetime.now(UTC)
            job.error_message = None
            await session.commit()
            _log.info("export_job %s ready (%d bytes)", job_id, len(pdf_bytes))
        except Exception as exc:
            _log.exception("export_job %s failed", job_id)
            # Освобождаем сессию от старого state на случай дёрнутого flush'а
            await session.rollback()
            # Перечитываем job: его status='running' мог потеряться при rollback.
            job = await session.get(PdfExportJob, job_id)
            if job is not None:
                job.status = "failed"
                # error_message — короткий машинный код для UI + класс ошибки;
                # полный трейс ушёл в логи, в БД пихать его смысла нет.
                job.error_message = f"{type(exc).__name__}: {exc}"[:500]
                await session.commit()


# ---------------------------------------------------------------------------
# GET status
# ---------------------------------------------------------------------------


async def get_export_job(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
) -> PdfExportJob:
    """Найти job пользователя; чужие job'ы → 404 (не 403, чтобы не
    утекало само существование чужого ID).
    """
    stmt = select(PdfExportJob).where(
        PdfExportJob.id == job_id, PdfExportJob.user_id == user_id
    )
    row = (await session.execute(stmt)).scalars().first()
    if row is None:
        raise ExportJobNotFoundError(f"export job {job_id} not found")
    return row


def signed_url_for(storage: Storage, *, pdf_key: str) -> str:
    """Создать короткоживущий URL для скачивания готового PDF.

    Сам TTL — `SIGNED_URL_TTL_SECONDS`; expires_at для ответа вычисляется
    отдельно в API-слое, чтобы один источник правды по времени.
    """
    return storage.signed_url(pdf_key, ttl_seconds=SIGNED_URL_TTL_SECONDS)


def signed_url_expires_at(now: datetime) -> datetime:
    """Истечение signed URL — `now + TTL`. Передаётся клиенту в ответе,
    чтобы UI знал, когда нужно перезапросить статус для freshURL."""
    from datetime import timedelta

    return now + timedelta(seconds=SIGNED_URL_TTL_SECONDS)


__all__ = [
    "SIGNED_URL_TTL_SECONDS",
    "SUPPORTED_SECTIONS",
    "ExportError",
    "ExportJobNotFoundError",
    "get_export_job",
    "normalize_sections",
    "process_export_job",
    "signed_url_expires_at",
    "signed_url_for",
    "start_export_job",
]
