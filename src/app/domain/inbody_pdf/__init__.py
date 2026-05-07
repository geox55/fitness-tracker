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

__all__ = [
    "ParsedInBody",
    "UnitsHint",
    "detect_template",
    "extract_fields",
    "is_inbody",
    "normalize_decimal",
]
