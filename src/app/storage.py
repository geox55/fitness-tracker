"""Object storage: интерфейс + S3 / in-memory реализации.

S3Storage работает с любым S3-совместимым endpoint (AWS S3, MinIO, R2,
Selectel) — boto3 одинаково. Если `s3_endpoint` пустой (например, в unit-
тестах) — выбирается InMemoryStorage.

Загрузка/удаление синхронные внутри (boto3 sync), вызываются из async-
обработчиков через asyncio.to_thread, чтобы не блокировать event loop.
"""

from __future__ import annotations

import threading
from functools import lru_cache
from typing import Protocol

import boto3
from botocore.client import Config as BotoConfig

from .config import Settings, get_settings


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


# ---- In-memory (для тестов) ----------------------------------------------


class InMemoryStorage:
    """Хранит блобы в dict. Thread-safe (на случай конкурентных async-задач
    в одном тесте). public_url отдаёт фейковый URL — тестам важно лишь, что
    он стабильный и парсится."""

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
