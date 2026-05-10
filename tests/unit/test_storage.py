"""Unit-тесты storage abstraction."""

from collections.abc import Iterator

import pytest

from app.config import Settings
from app.storage import InMemoryStorage, S3Storage, get_storage


class TestInMemoryStorage:
    @pytest.mark.asyncio
    async def test_put_returns_public_url(self) -> None:
        s = InMemoryStorage(public_base="http://test")
        url = await s.put(key="a/b.jpg", data=b"x", content_type="image/jpeg")
        assert url == "http://test/a/b.jpg"

    @pytest.mark.asyncio
    async def test_put_stores_bytes(self) -> None:
        s = InMemoryStorage()
        await s.put(key="k1", data=b"hello", content_type="text/plain")
        stored = s.get("k1")
        assert stored == (b"hello", "text/plain")

    @pytest.mark.asyncio
    async def test_delete_removes_key(self) -> None:
        s = InMemoryStorage()
        await s.put(key="k1", data=b"hello", content_type="text/plain")
        await s.delete(key="k1")
        assert s.get("k1") is None

    @pytest.mark.asyncio
    async def test_delete_missing_is_noop(self) -> None:
        s = InMemoryStorage()
        # Идемпотентно — не падает.
        await s.delete(key="never-existed")

    @pytest.mark.asyncio
    async def test_overwrite_replaces_data(self) -> None:
        s = InMemoryStorage()
        await s.put(key="k", data=b"v1", content_type="text/plain")
        await s.put(key="k", data=b"v2", content_type="text/plain")
        stored = s.get("k")
        assert stored is not None and stored[0] == b"v2"


class TestPublicUrl:
    def test_strips_leading_slash_in_key(self) -> None:
        s = InMemoryStorage(public_base="http://test")
        # Защита от двойного слэша при формировании URL.
        assert s.public_url("/a/b") == "http://test/a/b"


class TestSignedUrl:
    """Контракт signed_url для приватных объектов (NFR-04 spec 013).

    Реальную проверку подписи серверу InMemoryStorage не делает; здесь нам
    важно лишь, что:
    - URL формы public_url + query с подписью и expiry,
    - подпись детерминирована для одной пары (key, expires),
    - один и тот же key с разным expires → разные подписи.
    """

    def test_includes_expires_and_sig_query(self) -> None:
        s = InMemoryStorage(public_base="http://test")
        url = s.signed_url("a/b.pdf", ttl_seconds=60)

        assert url.startswith("http://test/a/b.pdf?")
        assert "expires=" in url
        assert "sig=" in url

    def test_different_keys_have_different_sigs(self) -> None:
        s = InMemoryStorage(public_base="http://test")
        url_a = s.signed_url("k1", ttl_seconds=60)
        url_b = s.signed_url("k2", ttl_seconds=60)
        # expires может совпасть (один тик); подпись — нет.
        sig_a = url_a.split("sig=")[1]
        sig_b = url_b.split("sig=")[1]
        assert sig_a != sig_b

    def test_default_ttl_is_five_minutes(self) -> None:
        # Контрактная защита: default TTL — 5 минут (NFR-04 spec 013).
        # Если кто-то сменит DEFAULT_SIGNED_URL_TTL_SECONDS — тест обнулит.
        from app.storage import DEFAULT_SIGNED_URL_TTL_SECONDS

        assert DEFAULT_SIGNED_URL_TTL_SECONDS == 300


class TestFactory:
    @pytest.fixture(autouse=True)
    def _clear_cache(self) -> Iterator[None]:
        get_storage.cache_clear()
        yield
        get_storage.cache_clear()

    def test_empty_endpoint_returns_in_memory(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app import storage as storage_mod

        monkeypatch.setattr(
            storage_mod,
            "get_settings",
            lambda: Settings(  # type: ignore[call-arg]
                database_url="postgresql+asyncpg://x:y@z/db",
                jwt_secret="x" * 32,
                s3_endpoint="",
            ),
        )
        assert isinstance(get_storage(), InMemoryStorage)

    def test_nonempty_endpoint_returns_s3(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app import storage as storage_mod

        monkeypatch.setattr(
            storage_mod,
            "get_settings",
            lambda: Settings(  # type: ignore[call-arg]
                database_url="postgresql+asyncpg://x:y@z/db",
                jwt_secret="x" * 32,
                s3_endpoint="http://minio:9000",
                s3_public_base_url="http://localhost:9000",
                s3_access_key="minio",
                s3_secret_key="minio12345",
                s3_bucket="test-bucket",
            ),
        )
        assert isinstance(get_storage(), S3Storage)
