"""PDF-import endpoints — spec 013 §9.

Все эндпоинты под общим префиксом `/inbody/measurements/from-pdf` —
визуально продолжают inbody-ресурс (см. spec 003).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ...domains.inbody.serializers import build_measurement_read
from ...domains.inbody_pdf.schemas import (
    ConfirmRequest,
    ConfirmResponse,
    JobRead,
    TemplateStatsResponse,
)
from ...domains.inbody_pdf.service import (
    MAX_PDF_BYTES,
    FileTooLargeError,
    JobAlreadyConfirmedError,
    JobNotFoundError,
    JobNotReadyError,
    confirm_import,
    get_job,
    start_import,
    template_stats,
)
from ...storage import get_storage
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(
    prefix="/inbody/measurements/from-pdf", tags=["inbody-pdf"]
)

# Отдельный роутер для отладочной статистики — лежит под /internal/inbody-pdf,
# чтобы выделять служебные ручки от пользовательских (spec 013 §9).
# Доступ — только авторизованным; ролевая модель (admin-only) появится отдельной
# задачей, когда добавим роли в `users`.
internal_router = APIRouter(
    prefix="/internal/inbody-pdf", tags=["inbody-pdf-internal"]
)


@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_pdf(
    user: CurrentUserDep,
    session: SessionDep,
    file: Annotated[UploadFile, File(...)],
) -> JobRead:
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_content_type",
                "message": "Ожидался application/pdf",
            },
        )
    data = await file.read()
    try:
        job = await start_import(
            session,
            user_id=user.id,
            file_bytes=data,
            storage=get_storage(),
        )
    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": exc.code,
                "message": f"Размер файла превышает {MAX_PDF_BYTES // 1024 // 1024} MB",
            },
        ) from exc
    return JobRead.model_validate(job)


@router.get("/{job_id}", response_model=JobRead)
async def get_pdf_job(
    job_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> JobRead:
    try:
        job = await get_job(session, user_id=user.id, job_id=job_id)
    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": exc.code, "message": "Задача импорта не найдена"},
        ) from exc
    return JobRead.model_validate(job)


@router.post("/{job_id}/confirm", response_model=ConfirmResponse)
async def confirm_pdf_job(
    job_id: uuid.UUID,
    payload: ConfirmRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> ConfirmResponse:
    try:
        measurement = await confirm_import(
            session,
            user_id=user.id,
            job_id=job_id,
            overrides=payload.overrides,
            measured_at=payload.measured_at,
        )
    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": exc.code, "message": "Задача импорта не найдена"},
        ) from exc
    except JobAlreadyConfirmedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": exc.code, "message": "Импорт уже подтверждён"},
        ) from exc
    except JobNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": exc.code,
                "message": "Не хватает данных для создания замера. Заполните вручную.",
            },
        ) from exc
    return ConfirmResponse(
        measurement=build_measurement_read(measurement, storage=get_storage())
    )


@internal_router.get(
    "/templates/stats", response_model=TemplateStatsResponse
)
async def templates_stats(
    _user: CurrentUserDep,
    session: SessionDep,
) -> TemplateStatsResponse:
    """REQ-09: счётчик распознанных шаблонов для аналитики покрытия парсера."""
    counts = await template_stats(session)
    return TemplateStatsResponse(templates_recognized=counts)
