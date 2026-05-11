"""PdfExportJob — spec 010 §3 Scenario 5 / REQ-10..12.

Async-flow:
1. POST /analytics/export-pdf → row(status='pending', sections=[...], from/to);
2. BackgroundTasks: status='running' → собрать данные → отрисовать PDF →
   загрузить в storage → status='ready' (pdf_key + ready_at) либо
   status='failed' (error_message).
3. GET /analytics/export-pdf/{job_id} → status; если ready, ещё и
   `signed_url` поверх `pdf_key` (TTL 1h из NFR-03).

Колонка `pdf_key` хранит ключ объекта в S3/MinIO, а не публичный URL —
URL даём подписанный с TTL.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base

ExportJobStatus = Literal["pending", "running", "ready", "failed"]


class PdfExportJob(Base):
    __tablename__ = "pdf_export_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[ExportJobStatus] = mapped_column(String, nullable=False)
    # Какие секции включать в отчёт; «список строк», а не bitmask, чтобы
    # схема была расширяема без миграций (добавили forecast/strength —
    # сразу можно слать в запросе).
    sections: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    # Диапазон отчёта; nullable — `from=None` означает «вся история» (REQ-10).
    period_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    # storage key готового PDF; null до status='ready'.
    pdf_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ready_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','running','ready','failed')",
            name="ck_pdf_export_status",
        ),
        Index("ix_pdf_export_user_created", "user_id", "created_at"),
    )
