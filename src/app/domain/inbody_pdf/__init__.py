"""Чистый PDF-парсер InBody — spec 013.

Здесь нет I/O и нет pdfplumber. На вход — `text: str` (уже извлечённый
текстовый слой), на выход — `ParsedInBody` со значениями полей,
`missing_fields`, `template`, `confidence`.

Сервис (`domains/inbody_pdf/service.py`) отвечает за извлечение текста
из PDF; парсер тестируется юнитами на сохранённых текстовых fixture'ах.
"""

from .parser import (
    ParsedInBody,
    UnitsHint,
    detect_template,
    extract_fields,
    is_inbody,
    normalize_decimal,
)
from .planner import (
    REQUIRED_FIELDS,
    ImportPlan,
    JobStatus,
    classify_status,
    has_required_fields,
    merge_for_confirmation,
    plan_import,
)

__all__ = [
    "REQUIRED_FIELDS",
    "ImportPlan",
    "JobStatus",
    "ParsedInBody",
    "UnitsHint",
    "classify_status",
    "detect_template",
    "extract_fields",
    "has_required_fields",
    "is_inbody",
    "merge_for_confirmation",
    "normalize_decimal",
    "plan_import",
]
