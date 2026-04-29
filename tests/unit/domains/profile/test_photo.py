"""Unit-тесты обработки фото профиля (spec 002 REQ-07)."""

import io

import pytest
from PIL import Image

from app.domains.profile.photo import (
    MAX_BYTES,
    TARGET_SIZE,
    PhotoInvalidError,
    PhotoTooLargeError,
    PhotoUnsupportedFormatError,
    process_image,
    validate_image_bytes,
)


def _png_bytes(width: int = 600, height: int = 400, mode: str = "RGB") -> bytes:
    img = Image.new(mode, (width, height), color=(120, 60, 200))
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def _jpeg_bytes(width: int = 600, height: int = 400) -> bytes:
    img = Image.new("RGB", (width, height), color=(20, 200, 80))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=80)
    return out.getvalue()


class TestValidate:
    def test_accepts_valid_png(self) -> None:
        img = validate_image_bytes(_png_bytes())
        assert img.format == "PNG"

    def test_accepts_valid_jpeg(self) -> None:
        img = validate_image_bytes(_jpeg_bytes())
        assert img.format == "JPEG"

    def test_rejects_non_image(self) -> None:
        with pytest.raises(PhotoInvalidError):
            validate_image_bytes(b"not an image at all")

    def test_rejects_too_large(self) -> None:
        # Не нужно реально генерить 5 MB картинку: padding-байтами.
        too_big = b"x" * (MAX_BYTES + 1)
        with pytest.raises(PhotoTooLargeError):
            validate_image_bytes(too_big)

    def test_rejects_gif_format(self) -> None:
        # GIF — реальный валидный image, но не разрешён в spec REQ-07.
        img = Image.new("P", (100, 100))
        out = io.BytesIO()
        img.save(out, format="GIF")
        with pytest.raises(PhotoUnsupportedFormatError):
            validate_image_bytes(out.getvalue())


class TestProcess:
    def test_output_is_target_size(self) -> None:
        img = validate_image_bytes(_png_bytes(width=800, height=600))
        result = process_image(img)
        check = Image.open(io.BytesIO(result))
        assert check.size == TARGET_SIZE

    def test_output_is_jpeg(self) -> None:
        img = validate_image_bytes(_png_bytes())
        result = process_image(img)
        check = Image.open(io.BytesIO(result))
        assert check.format == "JPEG"

    def test_landscape_center_cropped_to_square(self) -> None:
        # 800x400 пейзаж → центр-кроп до 400x400 → ресайз 512x512.
        img = validate_image_bytes(_png_bytes(width=800, height=400))
        result = process_image(img)
        check = Image.open(io.BytesIO(result))
        # Аспект = 1:1.
        assert check.size[0] == check.size[1]

    def test_portrait_center_cropped_to_square(self) -> None:
        img = validate_image_bytes(_png_bytes(width=400, height=800))
        result = process_image(img)
        check = Image.open(io.BytesIO(result))
        assert check.size[0] == check.size[1]

    def test_already_square_just_resized(self) -> None:
        img = validate_image_bytes(_png_bytes(width=1000, height=1000))
        result = process_image(img)
        check = Image.open(io.BytesIO(result))
        assert check.size == TARGET_SIZE

    def test_rgba_alpha_collapsed_to_white(self) -> None:
        # RGBA с прозрачным углом не должен крашить — должен схлопнуться на белый.
        img = Image.new("RGBA", (600, 600), (255, 0, 0, 0))
        out = io.BytesIO()
        img.save(out, format="PNG")
        validated = validate_image_bytes(out.getvalue())
        result = process_image(validated)
        # Не падает, возвращает валидный JPEG.
        check = Image.open(io.BytesIO(result))
        assert check.format == "JPEG"

    def test_grayscale_converted_to_rgb(self) -> None:
        img = Image.new("L", (600, 400), 200)
        out = io.BytesIO()
        img.save(out, format="PNG")
        validated = validate_image_bytes(out.getvalue())
        result = process_image(validated)
        check = Image.open(io.BytesIO(result))
        # JPEG может оказаться 'L' (Pillow сохраняет grayscale-JPEG), но size — 512.
        assert check.size == TARGET_SIZE
