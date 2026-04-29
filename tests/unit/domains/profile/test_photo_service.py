"""Unit-тесты сервисной части photo (без БД, с InMemoryStorage)."""

import io
import uuid

import pytest
from PIL import Image

from app.domains.profile.service import _extract_key_from_url
from app.storage import InMemoryStorage


def _png(width: int = 600, height: int = 400) -> bytes:
    img = Image.new("RGB", (width, height), color=(0, 100, 200))
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


class TestExtractKeyFromUrl:
    def test_extracts_key_from_minio_url(self) -> None:
        uid = uuid.uuid4()
        url = f"http://localhost:9000/fitness-uploads/profiles/{uid}/avatar.jpg"
        key = _extract_key_from_url(url)
        assert key == f"profiles/{uid}/avatar.jpg"

    def test_extracts_from_s3_style_url(self) -> None:
        uid = uuid.uuid4()
        url = f"https://my-bucket.s3.amazonaws.com/profiles/{uid}/avatar.jpg"
        key = _extract_key_from_url(url)
        assert key == f"profiles/{uid}/avatar.jpg"

    def test_returns_none_for_unrelated_url(self) -> None:
        # URL без префикса /profiles/ — не наш, оставляем orphan'ом.
        assert _extract_key_from_url("http://other.com/whatever.jpg") is None

    def test_returns_none_for_empty(self) -> None:
        assert _extract_key_from_url("") is None


class TestStorageRoundtrip:
    """Связка InMemoryStorage + сервис без БД: проверяем put/delete-логику
    отдельно от SQLAlchemy. Полные интеграционные тесты с реальной БД ещё
    впереди (testcontainers Postgres)."""

    @pytest.mark.asyncio
    async def test_put_stores_processed_image(self) -> None:
        s = InMemoryStorage()
        url = await s.put(
            key="profiles/u/avatar.jpg",
            data=_png(),
            content_type="image/jpeg",
        )
        assert url.endswith("profiles/u/avatar.jpg")
        stored = s.get("profiles/u/avatar.jpg")
        assert stored is not None
        assert stored[1] == "image/jpeg"

    @pytest.mark.asyncio
    async def test_delete_idempotent_after_double_call(self) -> None:
        s = InMemoryStorage()
        await s.put(key="k", data=b"v", content_type="image/jpeg")
        await s.delete(key="k")
        await s.delete(key="k")  # второй вызов не падает
        assert s.get("k") is None
