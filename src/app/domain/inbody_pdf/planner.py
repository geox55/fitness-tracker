"""Чистая логика «что делать с загруженным PDF» — spec 013.

Сервис (`domains/inbody_pdf/service.py`) держит работу с БД и storage,
сюда уезжают функции, которые не зависят ни от чего, кроме входного
текста и небольшого набора параметров. Это:

- `classify_status` — по результату парсинга решить, ready / partial / failed;
- `plan_import` — из текста и (опционально) overriding-статуса извлечения
  выдать один объект решения (статус + parsed + надо ли сохранять файл);
- `merge_for_confirmation` — собрать payload для создания InBodyMeasurement
  из распознанного и пользовательских правок, валидируя обязательное.

Все три — pure, тестируются без БД.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from .parser import ParsedInBody, extract_fields, is_inbody

JobStatus = Literal[
    "parsing",
    "ready",
    "partial",
    "failed",
    "not_inbody",
    "encrypted",
    "scanned_unsupported",
]

# Минимальный набор полей, который должен быть в job, чтобы пользователь
# мог создать измерение без ручного ввода. Соответствует REQ от spec 003.
REQUIRED_FIELDS: tuple[str, ...] = ("weight_kg", "body_fat_percent")


def classify_status(parsed: ParsedInBody) -> JobStatus:
    """`ready` — есть оба обязательных, `partial` — что-то одно, `failed` — пусто.

    Нужен ровно тот же критерий, который дальше использует
    `merge_for_confirmation`: иначе пользователь увидит «ready», а
    confirm упадёт. Поэтому ключи берём из REQUIRED_FIELDS.
    """
    if all(f in parsed.extracted for f in REQUIRED_FIELDS):
        return "ready"
    if parsed.extracted:
        return "partial"
    return "failed"


@dataclass(frozen=True)
class ImportPlan:
    """Что должна сделать оркестрация после anal'иза загруженного PDF."""

    status: JobStatus
    parsed: ParsedInBody | None
    # True — статус «ready»/«partial», файл сохраняем во временный storage.
    # False — для всех терминальных ошибок (not_inbody / encrypted / scanned /
    # failed): файл нам уже не нужен, в БД останется только запись об ошибке.
    persist_file: bool


def plan_import(
    *,
    text: str,
    status_override: JobStatus | None = None,
) -> ImportPlan:
    """Из извлечённого текста (или сообщения о невозможности извлечь)
    собрать план: какой выставить статус job'у и парсить ли поля.

    `status_override` — то, что вернул pdfplumber-уровень (`encrypted`
    или `scanned_unsupported`). Если он задан — текста или нет вовсе,
    или мы решили его игнорировать; парсер не запускаем.
    """
    if status_override is not None:
        return ImportPlan(status=status_override, parsed=None, persist_file=False)

    if not is_inbody(text):
        return ImportPlan(status="not_inbody", parsed=None, persist_file=False)

    parsed = extract_fields(text)
    status = classify_status(parsed)
    persist = status in ("ready", "partial")
    return ImportPlan(status=status, parsed=parsed, persist_file=persist)


def merge_for_confirmation(
    *,
    extracted: dict[str, Any],
    overrides: dict[str, Any] | None,
    measured_at: datetime,
) -> dict[str, Any]:
    """Слить распознанные поля + правки пользователя в payload для
    `inbody.service.create_manual` (см. spec 003).

    Поведение:
    - `measured_at` всегда первым ключом; чтобы overrides случайно его
      не затёрли, копируем последним и затем восстанавливаем.
    - overrides побеждают extracted (REQ-04: пользователь правит руками).
    - значения `None` в overrides трактуются как «удалить» — пользователь
      явно очистил поле на превью; полезно если парсер вытащил ерунду
      (например, неверный visceral_fat).
    """
    payload: dict[str, Any] = dict(extracted)
    if overrides:
        for k, v in overrides.items():
            if v is None:
                payload.pop(k, None)
            else:
                payload[k] = v
    payload["measured_at"] = measured_at
    return payload


def has_required_fields(payload: dict[str, Any]) -> bool:
    """True если payload пригоден для create_manual — оба обязательных поля
    присутствуют и не None.
    """
    return all(payload.get(f) is not None for f in REQUIRED_FIELDS)
