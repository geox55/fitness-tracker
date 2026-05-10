# Fitness Tracker

PWA-приложение для учёта физической активности и анализа InBody.

См. [`specs/`](specs/) и [`docs/architecture/`](docs/architecture/).

## Запуск локально

Требуется: Docker, Flutter SDK, `uv`.

```bash
make start              # поднимает Postgres, API, nginx, MinIO, Mailpit + миграции
                        # и запускает PWA в Chrome
```

`Ctrl+C` останавливает PWA; docker-сервисы остаются в фоне. `make stop`
останавливает всю инфру, `make down` — удаляет контейнеры (volumes сохраняются).

`make help` — полный список команд.

## Dev-команды

```bash
make test         # uv run pytest
make lint         # uv run ruff check .
make typecheck    # uv run mypy (на src/ + ml/etl/)
make check        # всё разом
make logs         # хвост логов docker-сервисов
make migrate      # применить alembic-миграции
make seed         # залить exercise catalog
make pdf-cleanup  # ручной запуск удаления просроченных PDF-импортов
```

## Фоновые процессы

`api-cleanup` — отдельный контейнер на образе API, поднимается вместе с
`make start`. Каждый час вызывает `app.scripts.inbody_pdf_cleanup`,
удаляющий из БД и storage неподтверждённые `pdf_import_jobs` старше 1 часа
(spec 013 REQ-08). Период регулируется переменной окружения
`PDF_CLEANUP_INTERVAL_SECONDS` (в секундах).

```bash
docker compose logs -f api-cleanup    # поток вызовов и их статус
make pdf-cleanup                       # вручную в текущем api-контейнере
```

## ML training pipeline (spec 008 + 012)

Главный AI-блок диплома Маши: своя ML-модель прогноза InBody-метрик на
1/2/4 недели. Pipeline отделён от прод-API дeп-группой `ml`, в рантайме
сервиса не активен, пока на диске нет обученного артефакта (см.
`src/app/domain/forecast/ml_predictor.py` — lazy-load с fallback к baseline).

```bash
# 1) Поставить ML-зависимости (numpy/pandas/sklearn/lightgbm/joblib).
make ml-deps

# 2) Скачать Kaggle-источники (вручную, см. ml/data/processed/LICENSES.md):
#    - https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset
#    - https://www.kaggle.com/datasets/fedesoriano/body-fat-prediction-dataset
#    Положить как ml/data/raw/gym_members_exercise.csv и ml/data/raw/bodyfat.csv.

# 3) Собрать Dataset-B inbody_timeseries (REQ-16 spec 012):
make ml-dataset

# 4) Обучить все три модели и получить сводную таблицу для главы диплома:
make ml-train       # persistence + ridge + lgbm + compare
# или только основную модель:
make ml-train-lgbm
```

Артефакты: `ml/models/inbody_pred/{model}/v{semver}/` (`*.joblib` +
`manifest.json`). При следующем рестарте API `ml_predictor.load_predictor()`
автоматически подхватит самую свежую версию `lgbm`-модели; service
переключится с baseline на ML, fallback срабатывает на любой ошибке
инференса (REQ-12 spec 008).
