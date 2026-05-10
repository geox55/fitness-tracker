"""Сериализация InBodyMeasurement → MeasurementRead.

Выделено отдельным модулем, потому что в read-DTO нужен `original_pdf_url`
как **signed URL** с коротким TTL — мы не можем просто `model_validate(orm)`,
т.к. в БД хранится только storage-key (NFR-04 spec 013).

Сюда же логично положить любые будущие энричмент-функции
(например, рассчитывать дельту к предыдущему замеру).
"""

from __future__ import annotations

from .models import InBodyMeasurement
from .schemas import MeasurementRead

# Локальный импорт типа Storage сделан отложенным внутри функции, чтобы
# избежать цикла import'ов на старте — ничего серьёзного.


def build_measurement_read(
    measurement: InBodyMeasurement,
    *,
    storage: object,
    pdf_url_ttl_seconds: int | None = None,
) -> MeasurementRead:
    """Собрать DTO с signed URL вместо storage-key.

    `storage` в типе оставляем `object`, чтобы модуль не тянул весь
    storage-стек; на практике сюда передают `app.storage.Storage`.
    """
    pdf_url: str | None = None
    if measurement.original_pdf_key:
        # Импорт лениво: модуль schemas нужен другим местам без storage.
        from ...storage import DEFAULT_SIGNED_URL_TTL_SECONDS

        ttl = pdf_url_ttl_seconds or DEFAULT_SIGNED_URL_TTL_SECONDS
        # `signed_url` — синхронный метод: подпись считается локально,
        # I/O нет.
        pdf_url = storage.signed_url(  # type: ignore[attr-defined]
            measurement.original_pdf_key, ttl_seconds=ttl
        )

    return MeasurementRead(
        id=measurement.id,
        user_id=measurement.user_id,
        measured_at=measurement.measured_at,
        weight_kg=float(measurement.weight_kg),
        height_cm=float(measurement.height_cm),
        sex=measurement.sex,
        body_fat_percent=float(measurement.body_fat_percent),
        muscle_mass_kg=(
            float(measurement.muscle_mass_kg)
            if measurement.muscle_mass_kg is not None
            else None
        ),
        body_water_percent=(
            float(measurement.body_water_percent)
            if measurement.body_water_percent is not None
            else None
        ),
        protein_kg=(
            float(measurement.protein_kg)
            if measurement.protein_kg is not None
            else None
        ),
        minerals_kg=(
            float(measurement.minerals_kg)
            if measurement.minerals_kg is not None
            else None
        ),
        visceral_fat_level=measurement.visceral_fat_level,
        bmr_kcal=measurement.bmr_kcal,
        fat_free_mass_kg=(
            float(measurement.fat_free_mass_kg)
            if measurement.fat_free_mass_kg is not None
            else None
        ),
        bmi=float(measurement.bmi),
        source=measurement.source,
        original_pdf_url=pdf_url,
        created_at=measurement.created_at,
    )
