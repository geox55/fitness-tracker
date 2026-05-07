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
make test       # uv run pytest
make lint       # uv run ruff check .
make typecheck  # uv run mypy (на src/ + ml/etl/)
make check      # всё разом
make logs       # хвост логов docker-сервисов
make migrate    # применить alembic-миграции
make seed       # залить exercise catalog
```
