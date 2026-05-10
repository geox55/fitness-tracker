"""Удаление просроченных pdf_import_jobs (REQ-08 spec 013).

Запускается из cron / Makefile / GitHub Actions раз в час:

    uv run python -m app.scripts.inbody_pdf_cleanup

Поведение:
- Находит job'ы старше TTL (по умолчанию 1 час) без `confirmed_at`.
- Удаляет соответствующие temp-файлы из object storage.
- Удаляет записи из БД одним DELETE.

Параметризуется флагами `--ttl-hours` и `--dry-run` для отладки.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..db import get_engine
from ..domains.inbody_pdf.models import PdfImportJob
from ..domains.inbody_pdf.service import TEMP_TTL, cleanup_expired_jobs
from ..storage import get_storage

_log = logging.getLogger("app.scripts.inbody_pdf_cleanup")


async def _count_expired(
    session_factory: async_sessionmaker[AsyncSession], *, cutoff: datetime
) -> int:
    async with session_factory() as session:
        stmt = select(PdfImportJob).where(
            PdfImportJob.confirmed_at.is_(None),
            PdfImportJob.created_at < cutoff,
        )
        rows = (await session.execute(stmt)).scalars().all()
        return len(rows)


async def _run(*, ttl: timedelta, dry_run: bool) -> int:
    now = datetime.now(UTC)
    sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False)

    if dry_run:
        n = await _count_expired(sessionmaker, cutoff=now - ttl)
        print(f"-> would delete {n} expired pdf_import_jobs", file=sys.stderr)
        return n

    async with sessionmaker() as session:
        deleted = await cleanup_expired_jobs(
            session, storage=get_storage(), now=now, ttl=ttl
        )
        await session.commit()
    print(f"-> deleted {deleted} expired pdf_import_jobs", file=sys.stderr)
    return deleted


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(description="Cleanup expired inbody PDF import jobs.")
    p.add_argument(
        "--ttl-hours",
        type=float,
        default=TEMP_TTL.total_seconds() / 3600,
        help=f"TTL в часах (default: {TEMP_TTL.total_seconds() / 3600:g})",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Только посчитать, ничего не удалять",
    )
    args = p.parse_args(argv)

    ttl = timedelta(hours=args.ttl_hours)
    asyncio.run(_run(ttl=ttl, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
