"""Object storage: интерфейс + S3 / in-memory реализации.

S3Storage работает с любым S3-совместимым endpoint (AWS S3, MinIO, R2,
Selectel) — boto3 одинаково. Если `s3_endpoint` пустой (например, в unit-
тестах) — выбирается InMemoryStorage.

Загрузка/удаление синхронные внутри (boto3 sync), вызываются из async-
обработчиков через asyncio.to_thread, чтобы не блокировать event loop.

`signed_url` — приватный доступ к объекту с ограниченным TTL: для
чувствительных артефактов (например, оригиналы InBody-PDF, NFR-04 spec 013)
используем именно его, а не `public_url`.
"""

from __future__ import annotations

import hashlib
import hmac
import threading
import time
from functools import lru_cache
from typing import Protocol
from urllib.parse import quote

import boto3
from botocore.client import Config as BotoConfig

from .config import Settings, get_settings

# TTL по умолчанию для signed URL — 5 минут (NFR-04 spec 013).
DEFAULT_SIGNED_URL_TTL_SECONDS = 300


class StorageError(Exception):
    pass


class ObjectNotFoundError(StorageError):
    pass


class Storage(Protocol):
    async def put(
        self, *, key: str, data: bytes, content_type: str
    ) -> str:
        """Загружает объект, возвращает публичный URL."""

    async def delete(self, *, key: str) -> None:
        """Удаляет объект. Идемпотентно: missing key — не ошибка."""

    def public_url(self, key: str) -> str:
        """URL для чтения (без подписи; bucket/папка должны быть публичны)."""

    def signed_url(
        self,
        key: str,
        *,
        ttl_seconds: int = DEFAULT_SIGNED_URL_TTL_SECONDS,
    ) -> str:
        """Временный URL для приватных объектов. TTL — в секундах."""


# ---- S3 / MinIO -----------------------------------------------------------


class S3Storage:
    """boto3-обёртка. Stateless после конструктора — клиент потокобезопасен.

    Endpoint и URL разделены: `endpoint` — куда ходит API (внутри docker-network
    это http://minio:9000), `public_base_url` — что отдаём клиенту (snaружи это
    http://localhost:9000). В production оба совпадают с CDN/публичным S3.
    """

    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.s3_bucket
        self._public_base = settings.s3_public_base_url.rstrip("/")
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint or None,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=BotoConfig(signature_version="s3v4"),
        )

    def public_url(self, key: str) -> str:
        return f"{self._public_base}/{self._bucket}/{key.lstrip('/')}"

    async def put(
        self, *, key: str, data: bytes, content_type: str
    ) -> str:
        import asyncio

        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return self.public_url(key)

    async def delete(self, *, key: str) -> None:
        import asyncio

        await asyncio.to_thread(
            self._client.delete_object, Bucket=self._bucket, Key=key
        )

    def signed_url(
        self,
        key: str,
        *,
        ttl_seconds: int = DEFAULT_SIGNED_URL_TTL_SECONDS,
    ) -> str:
        """boto3 generate_presigned_url. Метод GET, объект и bucket — наши.

        Возвращает URL в схеме `endpoint`/bucket/key с подписью; за TTL —
        ссылка возвращает 403. Это синхронный вызов boto3, но без I/O
        (только локальная подпись), так что async не нужен.
        """
        url = self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=ttl_seconds,
            HttpMethod="GET",
        )
        # Подменяем endpoint, если public_base_url отличается от endpoint
        # (актуально в dev: API ходит к minio:9000, клиент — к localhost:9000).
        # boto3 подписывает по endpoint_url, но host не входит в canonical
        # request, поэтому простая замена префикса безопасна.
        return _swap_host(url, self._public_base, self._client.meta.endpoint_url)


def _swap_host(url: str, new_base: str, old_base: str) -> str:
    """Подменить `old_base` на `new_base` в URL, если совпадает префикс.

    Используется S3Storage.signed_url, чтобы клиент получил адрес,
    который ему доступен (localhost), а не внутренний (minio:9000).
    """
    if not old_base or new_base.rstrip("/") == old_base.rstrip("/"):
        return url
    if url.startswith(old_base.rstrip("/")):
        return new_base.rstrip("/") + url[len(old_base.rstrip("/")) :]
    return url


# ---- In-memory (для тестов) ----------------------------------------------


class InMemoryStorage:
    """Хранит блобы в dict. Thread-safe (на случай конкурентных async-задач
    в одном тесте). public_url отдаёт фейковый URL — тестам важно лишь, что
    он стабильный и парсится.

    `signed_url` имитирует подпись: добавляет HMAC-сигнатуру и unix-timestamp
    expiry в query string. Так тесты могут проверить, что URL отличается от
    public и содержит ожидаемые параметры, без поднятия настоящего S3.
    """

    # Симметричный секрет «по умолчанию» — для тестов и dev. В production
    # InMemoryStorage не используется; реальный подпис — у S3Storage.
    _SIGNING_KEY = b"in-memory-signing-key"

    def __init__(self, *, public_base: str = "http://memory-storage") -> None:
        self._objects: dict[str, tuple[bytes, str]] = {}
        self._lock = threading.Lock()
        self._public_base = public_base.rstrip("/")

    def public_url(self, key: str) -> str:
        return f"{self._public_base}/{key.lstrip('/')}"

    async def put(
        self, *, key: str, data: bytes, content_type: str
    ) -> str:
        with self._lock:
            self._objects[key] = (data, content_type)
        return self.public_url(key)

    async def delete(self, *, key: str) -> None:
        with self._lock:
            self._objects.pop(key, None)

    def signed_url(
        self,
        key: str,
        *,
        ttl_seconds: int = DEFAULT_SIGNED_URL_TTL_SECONDS,
    ) -> str:
        expires = int(time.time()) + int(ttl_seconds)
        # Подпись — HMAC по `key|expires`. Этого достаточно для тестов,
        # которые проверяют форму URL; реальную проверку подписи серверу
        # InMemoryStorage не реализует — он не отдаёт данные через HTTP.
        msg = f"{key}|{expires}".encode()
        sig = hmac.new(self._SIGNING_KEY, msg, hashlib.sha256).hexdigest()
        return f"{self.public_url(key)}?expires={expires}&sig={quote(sig)}"

    # ---- helpers для тестов (не часть Protocol) ---------------------------

    def get(self, key: str) -> tuple[bytes, str] | None:
        with self._lock:
            return self._objects.get(key)

    def list_keys(self) -> list[str]:
        with self._lock:
            return sorted(self._objects)


# ---- Factory --------------------------------------------------------------


@lru_cache(maxsize=1)
def get_storage() -> Storage:
    settings = get_settings()
    if not settings.s3_endpoint:
        return InMemoryStorage()
    return S3Storage(settings)
