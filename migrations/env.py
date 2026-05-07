"""Alembic env: async-режим. Берём DSN из настроек приложения."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Импорт моделей — Alembic должен видеть метаданные.
from app.config import get_settings
from app.db import Base
from app.domains.auth import models  # noqa: F401  (ensure tables registered)
from app.domains.catalog import models as _catalog_models  # noqa: F401
from app.domains.forecast import models as _forecast_models  # noqa: F401
from app.domains.inbody import models as _inbody_models  # noqa: F401
from app.domains.notifications import models as _notif_models  # noqa: F401
from app.domains.profile import models as _profile_models  # noqa: F401
from app.domains.workouts import models as _workouts_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# DSN из настроек переопределяет alembic.ini
config.set_main_option("sqlalchemy.url", get_settings().database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
