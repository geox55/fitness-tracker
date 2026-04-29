"""Фикстуры для integration-тестов: реальный Postgres через testcontainers,
изолированный per-test через nested transaction (savepoint) с rollback.

Архитектура:
- session-scope: контейнер postgres + engine + миграции (стартует один раз).
- function-scope: соединение, открывает SAVEPOINT перед тестом и rollback'ит
  после. Это даёт изоляцию без пересоздания схемы между тестами.
- TestClient использует override `get_session`, который выдаёт ту же сессию,
  привязанную к текущему savepoint.

Пометка: маркируем все тесты в директории как `integration` через
`pytest_collection_modifyitems` ниже — не нужно ставить декоратор вручную.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.config import get_settings
from app.db import get_session
from app.email import get_email_sender
from app.main import create_app
from app.storage import get_storage

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Все тесты в tests/integration/ автоматически получают marker 'integration'."""
    for item in items:
        if "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def _postgres_container() -> Iterator[PostgresContainer]:
    """Один Postgres-контейнер на всю pytest-сессию."""
    with PostgresContainer(
        "postgres:16-alpine",
        username="test",
        password="test",
        dbname="test",
        driver=None,
    ) as pg:
        yield pg


@pytest.fixture(scope="session")
def _database_url(_postgres_container: PostgresContainer) -> str:
    """Async DSN для приложения. testcontainers даёт sync-DSN — заменим драйвер."""
    raw = _postgres_container.get_connection_url()
    # testcontainers возвращает 'postgresql+psycopg2://...' или 'postgresql://...'
    # — приводим к asyncpg.
    if raw.startswith("postgresql+psycopg2://"):
        return raw.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if raw.startswith("postgresql://"):
        return raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    return raw


@pytest.fixture(scope="session", autouse=True)
def _configure_settings(_database_url: str) -> Iterator[None]:
    """Подменяем env до импорта/использования Settings, чтобы lru_cache получил
    тестовый DSN. Также чистим JWT_SECRET и SMTP-флаги."""
    overrides = {
        "DATABASE_URL": _database_url,
        "JWT_SECRET": "test-secret-with-enough-length-for-hs256-key",
        "ENV": "test",
        # Email — LoggingEmailSender, storage — InMemory.
        "SMTP_HOST": "",
        "S3_ENDPOINT": "",
    }
    saved = {k: os.environ.get(k) for k in overrides}
    os.environ.update(overrides)
    # Сбрасываем кэш Settings и factory-функций.
    get_settings.cache_clear()
    get_email_sender.cache_clear()
    get_storage.cache_clear()
    yield
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    get_settings.cache_clear()
    get_email_sender.cache_clear()
    get_storage.cache_clear()


@pytest.fixture(scope="session")
def _alembic_config(_database_url: str) -> AlembicConfig:
    cfg = AlembicConfig(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", _database_url)
    return cfg


@pytest.fixture(scope="session", autouse=True)
def _run_migrations(_configure_settings: None, _alembic_config: AlembicConfig) -> None:
    """Прогоняем миграции до head один раз на session."""
    # Alembic env.py читает get_settings(), который уже подменён через env.
    command.upgrade(_alembic_config, "head")


@pytest.fixture(scope="session")
async def _engine(_database_url: str, _run_migrations: None) -> AsyncIterator[None]:
    engine = create_async_engine(_database_url, pool_pre_ping=True)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(_engine) -> AsyncIterator[AsyncSession]:
    """Каждая функция получает чистую сессию: savepoint в начале, rollback в конце.

    Это в разы быстрее, чем drop/create-таблиц или TRUNCATE на каждом тесте,
    и при этом изолирует тесты полностью.
    """
    async with _engine.connect() as connection:
        trans = await connection.begin()
        sessionmaker = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            # SAVEPOINT-паттерн: session.commit() в обвязке коммитит SAVEPOINT,
            # а внешний rollback в финале возвращает БД в чистое состояние.
            # Без этого session.commit() рушит изоляцию между тестами.
            join_transaction_mode="create_savepoint",
        )
        async with sessionmaker() as session:
            try:
                yield session
            finally:
                await trans.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """httpx AsyncClient с FastAPI-приложением и подменённой сессией.

    LifespanManager нужен на случай startup/shutdown handlers — у нас их пока
    нет, но это правильный паттерн для asgi-приложений в тестах.
    """
    app = create_app()

    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        # Внутри тестов session.commit() оставляет данные видимыми для последующих
        # запросов в рамках того же теста, но всё равно откатится после теста
        # благодаря внешней транзакции в db_session.
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_session] = _override_get_session

    transport = ASGITransport(app=app)
    async with (
        LifespanManager(app),
        AsyncClient(transport=transport, base_url="http://testserver") as ac,
    ):
        yield ac
