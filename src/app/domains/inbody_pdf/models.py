"""PdfImportJob — spec 013 §6.

Job хранится в БД, оригинальный PDF лежит во временном storage до
подтверждения пользователем (REQ-07/08). После confirm создаётся
`InBodyMeasurement(source='pdf')` с `original_pdf_url`, ссылающимся на
постоянное хранилище.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base

JobStatus = Literal[
    "parsing",
    "ready",
    "partial",
    "failed",
    "not_inbody",
    "encrypted",
    "scanned_unsupported",
]


class PdfImportJob(Base):
    __tablename__ = "pdf_import_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[JobStatus] = mapped_column(String, nullable=False)
    template: Mapped[str | None] = mapped_column(String(32), nullable=True)
    extracted: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    confidence: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    missing_fields: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    # Где лежит PDF до confirm — внутренний storage key, не публичный URL.
    temp_pdf_key: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('parsing','ready','partial','failed',"
            "'not_inbody','encrypted','scanned_unsupported')",
            name="ck_pdf_job_status",
        ),
        Index("ix_pdf_job_user_created", "user_id", "created_at"),
    )
