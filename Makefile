# Fitness Tracker — dev Makefile
#
# Главная команда — `make start`: одной строкой поднимает всё локально.
# Сначала docker-compose (Postgres + API + nginx + MinIO + Mailpit + миграции
# через api-migrate), затем Flutter PWA в Chrome. Ctrl+C останавливает PWA;
# docker-сервисы продолжают работать в фоне — для полной остановки `make stop`.
#
# По умолчанию таргеты тихие; для отладки запускайте с `make V=1 <target>`.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# --- Параметры окружения ---------------------------------------------------

COMPOSE        ?= docker compose
COMPOSE_FILE   ?= docker-compose.yml
ENV_FILE       ?= .env
ENV_EXAMPLE    ?= .env.example
API_HEALTH_URL ?= http://localhost:8080/api/v1/health
API_BASE_URL   ?= http://localhost:8080/api/v1

# Сервисы compose, которые не относятся к PWA — поднимаются `make start`.
COMPOSE_SERVICES := postgres api api-migrate nginx minio minio-init mailpit

# --- Утилиты ---------------------------------------------------------------

# Тихий echo, печатает заголовок этапа.
define section
	@printf "\033[1;36m▶ %s\033[0m\n" "$(1)"
endef

# --- Целеуказатели ---------------------------------------------------------

.PHONY: help start stop down restart logs ps env \
        pwa migrate seed shell-db shell-api \
        test lint typecheck check rebuild clean

help: ## Показать список команд
	@awk 'BEGIN {FS = ":.*##"; printf "Команды:\n"} \
		/^[a-zA-Z_-]+:.*?##/ {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# --- Главное: всё локально -------------------------------------------------

start: env up wait-api migrate-info pwa ## Поднять всё локально (docker + PWA)

# `up` поднимает сервисы в фоне; `pwa` потом запустит Flutter в foreground.
.PHONY: up wait-api migrate-info
up:
	$(call section,Поднимаем docker-сервисы (postgres / api / nginx / minio / mailpit))
	@$(COMPOSE) -f $(COMPOSE_FILE) up -d --remove-orphans

wait-api:
	$(call section,Ждём пока API ответит на /health)
	@for i in $$(seq 1 60); do \
		if curl -fsS $(API_HEALTH_URL) >/dev/null 2>&1; then \
			printf "\033[32m✓ API готов\033[0m\n"; exit 0; \
		fi; sleep 1; \
	done; \
	printf "\033[31m✗ API не поднялся за 60 секунд\033[0m\n"; \
	$(COMPOSE) -f $(COMPOSE_FILE) logs --tail=80 api; \
	exit 1

migrate-info:
	@printf "\033[2mМиграции применяет сервис api-migrate в compose; статус — %s\033[0m\n" \
		"`$(COMPOSE) -f $(COMPOSE_FILE) ps api-migrate --format json | head -1 | grep -o 'State[^,]*' || echo 'check `make logs`'`"

pwa: ## Flutter web (Chrome). Останавливается Ctrl+C.
	$(call section,Запускаем PWA: flutter run -d chrome)
	@cd pwa && flutter run -d chrome --dart-define=API_BASE_URL=$(API_BASE_URL)

# --- Управление инфрой -----------------------------------------------------

stop: ## Остановить docker-сервисы (volumes сохраняются)
	$(call section,docker compose stop)
	@$(COMPOSE) -f $(COMPOSE_FILE) stop

down: ## Остановить и удалить контейнеры (volumes сохраняются)
	$(call section,docker compose down)
	@$(COMPOSE) -f $(COMPOSE_FILE) down

restart: ## Перезапустить все сервисы
	@$(COMPOSE) -f $(COMPOSE_FILE) restart

logs: ## Хвост логов всех сервисов (Ctrl+C для выхода)
	@$(COMPOSE) -f $(COMPOSE_FILE) logs -f --tail=100

ps: ## Статус сервисов
	@$(COMPOSE) -f $(COMPOSE_FILE) ps

env: ## Создать .env из .env.example, если ещё нет
	@if [ ! -f $(ENV_FILE) ]; then \
		cp $(ENV_EXAMPLE) $(ENV_FILE); \
		printf "\033[33m✦ Создан $(ENV_FILE) из $(ENV_EXAMPLE) — проверьте JWT_SECRET\033[0m\n"; \
	fi

# --- Бэкенд: миграции, сидинг, шеллы --------------------------------------

migrate: ## Применить миграции (внутри контейнера api)
	$(call section,alembic upgrade head)
	@$(COMPOSE) -f $(COMPOSE_FILE) run --rm api-migrate

seed: ## Залить упражнения в каталог (idempotent)
	$(call section,Сидим exercise catalog)
	@$(COMPOSE) -f $(COMPOSE_FILE) exec api python -m app.scripts.seed_exercises

shell-db: ## psql-сессия в Postgres
	@$(COMPOSE) -f $(COMPOSE_FILE) exec postgres \
		psql -U $${POSTGRES_USER:-app} -d $${POSTGRES_DB:-fitness}

shell-api: ## bash в контейнере api
	@$(COMPOSE) -f $(COMPOSE_FILE) exec api bash

# --- Локальные проверки (без docker) --------------------------------------

test: ## pytest всё
	@uv run pytest tests/ -q

lint: ## ruff
	@uv run ruff check .

typecheck: ## mypy на src/ + ml/etl/
	@uv run mypy
	@uv run mypy ml/etl/inbody/ --strict

check: lint typecheck test ## Все локальные проверки

# --- Полный пересбор -------------------------------------------------------

rebuild: ## Пересобрать api-образ (после изменений deploy/api/Dockerfile)
	@$(COMPOSE) -f $(COMPOSE_FILE) build api

clean: ## Снести контейнеры И volumes (потеряете данные!)
	@printf "\033[31m⚠ Это удалит pgdata и miniodata. Ctrl+C чтобы отменить.\033[0m\n"
	@sleep 3
	@$(COMPOSE) -f $(COMPOSE_FILE) down -v
