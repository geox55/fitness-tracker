# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Что это

PWA для учёта тренировок + анализа InBody с двумя ML-моделями (генератор плана и предиктор InBody). Спека-ориентированная разработка: каждая фича описана в `specs/NNN-*.md`, и код должен соответствовать REQ/NFR оттуда. `specs/000-overview.md` — индекс; `docs/architecture/` — high-level картина системы.

## Команды

Все рутинные операции — через `make`; goal по умолчанию печатает список.

| | |
|---|---|
| `make start` | docker (postgres / api / nginx / minio / mailpit / api-cleanup) + миграции + `flutter run -d chrome` |
| `make stop` / `make down` | стоп контейнеров / удалить контейнеры (volumes остаются) |
| `make test` | `uv run pytest tests/ -q` |
| `make lint` | `uv run ruff check .` |
| `make typecheck` | `uv run mypy` (strict на `src/`) + `mypy --strict ml/etl/inbody/` |
| `make check` | lint + typecheck + test |
| `make migrate` | `alembic upgrade head` через `api-migrate` |
| `make seed` | сидинг exercise catalog (идемпотентно) |
| `make pdf-cleanup` | вручную удалить просроченные `pdf_import_jobs` (spec 013 REQ-08) |
| `make shell-db` / `make shell-api` | psql / bash внутри контейнера |
| `make monitoring-up` / `monitoring-down` / `monitoring-logs` | Prometheus + Grafana (сеть `fitness-tracker_internal`, см. `deploy/README.md`) |

Один тест: `uv run pytest tests/integration/test_plans.py::TestPlanGeneration::test_generate_happy_path_returns_four_weeks -v`. Маркеры `unit` / `integration` проставляются автоматически по пути (`tests/integration/` → `integration`).

ML pipeline отделён группой зависимостей `ml`:

- `make ml-deps` — `uv sync --group ml`
- `make ml-dataset` / `make ml-train` / `make ml-train-lgbm` — InBody-предиктор (spec 008 + 012)
- `make ml-rec-dataset` / `make ml-rec-train` — workout-recommender (spec 006 + 012)

Артефакты складываются в `ml/models/<task>/<algo>/v<semver>/` (`*.joblib` + `manifest.json`). Прод-API подхватит свежую `lgbm`-версию через `ml_predictor.load_predictor()` при рестарте; на любой ошибке инференса срабатывает baseline fallback (REQ-12 spec 008). Без артефакта на диске сервис работает на baseline — `lightgbm`/`joblib` не нужны в прод-образе.

## Архитектура бэкенда (`src/app/`)

FastAPI + SQLAlchemy 2 (async) + Alembic. Слои:

```
api/v1/<feature>.py   — тонкие HTTP-эндпоинты, маппинг исключений → HTTP, schemas
domains/<feature>/    — БД-обвязка (models.py, schemas.py, service.py, serializers.py)
domain/<feature>/     — чистая логика без I/O, тестируется юнитами
```

Граница между `domain/` (pure) и `domains/` (БД) — жёсткая. Composer плана (`domain/workout_generator/composer.py`) принимает `ExercisePool` dataclass'ы и возвращает `PlannedPlan` — никаких ORM. Сервис (`domains/plan/service.py`) грузит каталог из БД, превращает в pool, дёргает composer, persistит результат. Это даёт быстрые юнит-тесты на сложную логику (см. `tests/unit/domain/workout_generator/test_composer.py`).

Все маршруты регистрируются в `src/app/main.py::create_app` под общим префиксом `settings.api_v1_prefix` (`/api/v1`). Сессия БД — `get_session()` через FastAPI Depends (`SessionDep`); коммит/rollback в обвязке. Фоновые задачи (`BackgroundTasks`) получают `get_sessionmaker()`, потому что dependency-session закроется до их запуска (см. `analytics/export_service.py::process_export_job` как образец).

Storage — `app.storage.Storage` (S3 через boto3 или InMemory в тестах); `signed_url()` синхронный, без I/O. Для приватных файлов (фото профиля, оригиналы InBody PDF, экспортированные отчёты) в БД хранится **storage key**, а не URL — signed URL пересоздаётся на каждый GET (`MeasurementRead.original_pdf_url`, `WorkoutPlan`-нет, `pdf_export_jobs.pdf_key`). TTL — 1 час для отчётов (NFR-03 spec 010), 5 мин для InBody-оригиналов (spec 013).

Миграции в `migrations/versions/0001..0015`, нумерация инкрементная без gap'ов. Новые модели регистрируются в `migrations/env.py` через `from app.domains.X import models as _X_models  # noqa: F401`, иначе Alembic не увидит таблицу. Один active план на пользователя гарантируется partial unique index (`uq_workout_plans_one_active`).

## Архитектура PWA (`pwa/lib/`)

Flutter web + Riverpod + go_router + Dio. Слои:

```
app/             — router, theme, l10n bootstrap
data/api/        — Dio-клиенты + DTO + Riverpod providers (AsyncValue)
features/<area>/ — экраны и виджеты
ui/              — переиспользуемые виджеты (если есть)
```

API-клиент шаблон:
1. DTO с `fromJson(Map<String, dynamic>)`, без code-gen — schemas стабильные, json_serializable не нужен.
2. Метод-обёртка ловит `DioException` и мапит через `mapDioToFailure(e)` → `AppFailure` (sealed). Специфические 4xx (например, `preconditions_not_met` у `/plans/generate`) разбираются по `response.data['detail']['error']` и поднимаются как `ApiFailure(code: ...)`.
3. Provider — `FutureProvider.autoDispose` (single resource) или `.family<T, Args>` (параметризованный); `Args`-класс с `==`/`hashCode`, иначе Riverpod не закеширует.

`AppFailure` объявлен sealed внутри `data/api/failure.dart` — наследоваться из других файлов нельзя, новые типы добавлять туда же.

Аутентификация: рефреш-токены хранятся в `shared_preferences` (на web — localStorage). `AuthStorage` инициализируется до `runApp` и инжектится через override `authStorageProvider` (см. `main.dart`). Ротация рефреш-токенов с reuse-detection — reused приоритетнее expired.

Открыть signed URL в новой вкладке: `package:web` (`web.window.open(url, '_blank')`) — без `url_launcher`, web-only достаточно для PWA.

## ML pipeline

Две независимые модели; обе живут вне runtime-критического пути.

- **InBody predictor** (spec 008, Маша) — рекурсивный one-step quantile LightGBM. ETL — `ml/etl/inbody/` (Kaggle S3+S4 → Dataset-B). Training — `ml/training/inbody_timeseries/{persistence,train_ridge,train_lgbm}.py`; `compare.py` собирает MD-таблицу метрик для главы диплома. Сервинг — `src/app/domain/forecast/ml_predictor.py` с lazy-load и baseline fallback.
- **Workout recommender** (spec 006, Егор) — popularity / LR / LightGBM ранкер упражнений. ETL — `ml/etl/workout_recommender/`. Training — `ml/training/workout_recommender/`. **Не подключён в API** (rule-based composer полностью покрывает REQ-16 fallback и используется как primary path).

## Тесты

`pytest-asyncio` в `auto` mode. Интеграция — testcontainers Postgres один на сессию + savepoint per test (`tests/integration/conftest.py`). FastAPI берёт ту же сессию через `app.dependency_overrides[get_session]`, чтобы видеть savepoint'ные данные. Это значит: в тестах **нельзя ожидать**, что `BackgroundTasks` дёрнут свой собственный sessionmaker — `get_sessionmaker` тоже переопределён и возвращает ту же сессию (см. `process_export_job` для образца).

Юнит-тесты `domain/` — чистый pytest без фикстур БД, должны быть быстрыми (<100 мс на тест).

## Конвенции

- Все комментарии и docstrings — на русском, описывают **«почему»**, а не **«что»**. Спецификационные требования цитируются по тегу (REQ-NN spec NNN), это якорь для будущих изменений.
- Спека > код: если код противоречит спеке — править код. Если спека устарела — править спеку (см. memories: `010` и `013` имели хвостовые REQ, добавленные итеративно).
- Не дублировать `domain/` <→ `domains/`: если функция чистая и не лезет в БД, она живёт в `domain/`. Это упрощает мокирование и юнит-тесты.
- Альтернативы и edge cases в спеке расписаны в §3 (User Scenarios) и §10 (Edge Cases) — там же ищите ожидаемое поведение перед фиксом «бага».

## Что НЕ делать без обсуждения

- Менять схему БД без миграции (никаких `Base.metadata.create_all()`).
- Класть в `input_features` JSONB (план / job-ы) PII — это снапшоты для retraining (NFR-04 spec 006).
- Переключать прод-API на ML-инференс при отсутствии артефакта — baseline предсказуемее и быстрее.
- Использовать `url_launcher` или другие тяжёлые pwa-пакеты, когда `package:web` решает.
