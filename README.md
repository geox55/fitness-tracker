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
