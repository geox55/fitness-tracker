FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Установим uv
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

WORKDIR /app

# Сначала копируем только манифесты, чтобы кешировать слой зависимостей.
# README.md нужен hatchling для валидации метаданных пакета.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# Затем — код
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini

# Каталог упражнений нужен миграции 0016_seed_full_catalog и скрипту
# seed_exercises (см. src/app/scripts/seed_exercises.py:33 и
# migrations/versions/0016_seed_full_catalog.py:43). В dev compose это
# bind-mount ./ml/data/processed, в prod-образ файл запекаем — 885 KB
# не страшно, зато миграции работают на любом сервере без mount'ов.
COPY ml/data/processed/exercises_catalog_ru.json ./ml/data/processed/exercises_catalog_ru.json

# Установим сам пакет
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
