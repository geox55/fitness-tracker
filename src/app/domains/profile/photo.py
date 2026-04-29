"""Обработка фото профиля — spec 002 REQ-07/REQ-08.

Чистые функции (`validate_image_bytes`, `process_image`) не делают I/O — всё
тестируется в памяти. Storage-операции — в сервисе сверху.
"""

from __future__ import annotations

import io
from typing import Final

from PIL import Image, UnidentifiedImageError

# spec 002 REQ-07: JPG/PNG, ≤5 MB, автообрезка до 512×512.
MAX_BYTES: Final = 5 * 1024 * 1024
TARGET_SIZE: Final = (512, 512)
ALLOWED_FORMATS: Final = frozenset({"JPEG", "PNG"})

# Конкретный MIME, которым кладём в storage. Сохраняем как JPEG для предсказуемого
# веса; альфа-канал PNG теряется (для аватара 512×512 — приемлемая компрессия).
OUTPUT_CONTENT_TYPE: Final = "image/jpeg"
OUTPUT_FORMAT: Final = "JPEG"
OUTPUT_QUALITY: Final = 85


class PhotoError(Exception):
    code: str = "photo_error"
    http_status: int = 400


class PhotoTooLargeError(PhotoError):
    code = "photo_too_large"
    http_status = 413


class PhotoUnsupportedFormatError(PhotoError):
    code = "photo_unsupported_format"
    http_status = 415


class PhotoInvalidError(PhotoError):
    code = "photo_invalid"
    http_status = 400


def validate_image_bytes(data: bytes) -> Image.Image:
    """Проверить размер и формат, вернуть PIL.Image. Не делает ресайз."""
    if len(data) > MAX_BYTES:
        raise PhotoTooLargeError(
            f"file is {len(data)} bytes, max is {MAX_BYTES}"
        )
    try:
        # Image.open ленивый; verify() читает заголовок, но "ломает" объект,
        # после чего нужно открыть заново. Это паттерн из Pillow docs.
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()
        image = Image.open(io.BytesIO(data))
    except UnidentifiedImageError as exc:
        raise PhotoInvalidError("not a valid image") from exc
    except (OSError, ValueError) as exc:
        # Pillow бросает OSError для повреждённых данных, ValueError для
        # неподдерживаемых параметров — оба значат "не парсится".
        raise PhotoInvalidError(f"image decode failed: {exc}") from exc
    if image.format not in ALLOWED_FORMATS:
        raise PhotoUnsupportedFormatError(
            f"format {image.format!r} not in {sorted(ALLOWED_FORMATS)}"
        )
    return image


def process_image(image: Image.Image) -> bytes:
    """Center-crop до квадрата + ресайз до TARGET_SIZE. JPEG, quality 85."""
    # 1. Конвертим в RGB (JPEG не поддерживает альфу; PNG с прозрачностью
    #    схлопывается на белый фон).
    if image.mode not in ("RGB", "L"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "RGBA":
            background.paste(image, mask=image.split()[3])
        else:
            background.paste(image.convert("RGBA"))
        image = background
    elif image.mode == "L":
        image = image.convert("RGB")

    # 2. Center-crop до квадрата по короткой стороне.
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    image = image.crop((left, top, left + side, top + side))

    # 3. Ресайз с антиалиасингом.
    image = image.resize(TARGET_SIZE, Image.Resampling.LANCZOS)

    out = io.BytesIO()
    image.save(out, format=OUTPUT_FORMAT, quality=OUTPUT_QUALITY, optimize=True)
    return out.getvalue()
