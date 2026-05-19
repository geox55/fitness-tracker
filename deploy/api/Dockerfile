FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Установим uv
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

# libgomp1 — OpenMP runtime, обязательная зависимость lightgbm. В
# python:3.12-slim её нет, и без неё `import lightgbm` валится с
# OSError: libgomp.so.1: cannot open shared object file.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала копируем только манифесты, чтобы кешировать слой зависимостей.
# README.md нужен hatchling для валидации метаданных пакета.
# Группа ml включена в прод-образ: lightgbm/joblib/sklearn нужны
# runtime'у для инференса InBody-предиктора и workout-recommender'а
# (см. src/app/domain/forecast/ml_predictor.py и
# src/app/domain/workout_generator/recommender.py).
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev --group ml

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

# ML-артефакты обученных моделей (~2.2 МБ): InBody-предиктор + workout
# recommender. Без них load_predictor() / load_ranker() вернут None,
# и сервис уйдёт в baseline-фолбэк.
COPY ml/models ./ml/models

# Установим сам пакет
RUN uv sync --frozen --no-dev --group ml

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
