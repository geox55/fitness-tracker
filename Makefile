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
# Имя `nginx` исторически сохранилось — образ под капотом теперь Angie
# (см. docker-compose.yml), но переименовывать сервис ради этого не стали.
COMPOSE_SERVICES := postgres api api-migrate api-cleanup nginx minio minio-init mailpit

# --- Утилиты ---------------------------------------------------------------

# Тихий echo, печатает заголовок этапа.
define section
	@printf "\033[1;36m▶ %s\033[0m\n" "$(1)"
endef

# --- Целеуказатели ---------------------------------------------------------

.PHONY: help start stop down restart logs ps env \
        pwa migrate seed pdf-cleanup shell-db shell-api \
        ml-deps ml-dataset ml-train ml-train-lgbm ml-compare \
        ml-rec-dataset ml-rec-train ml-rec-compare \
        test lint typecheck check rebuild clean \
        build-pwa build-api deploy deploy-sync deploy-image deploy-logs

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

seed: ## Залить полный каталог упражнений (873 с переводами, idempotent)
	$(call section,Сидим exercise catalog (ru + en, 873 упр.))
	@$(COMPOSE) -f $(COMPOSE_FILE) exec api python -m app.scripts.seed_exercises $(SEED_PATH)

pdf-cleanup: ## Удалить просроченные pdf_import_jobs (REQ-08, spec 013)
	$(call section,Чистим неподтверждённые PDF-импорты)
	@$(COMPOSE) -f $(COMPOSE_FILE) exec api python -m app.scripts.inbody_pdf_cleanup

# --- ML training pipeline (spec 008 + 012, главный AI-блок диплома) -------

ML_DATASET ?= ml/data/processed/dataset_b_inbody_timeseries.csv
ML_MODELS_ROOT ?= ml/models/inbody_pred
ML_VERSION ?= 0.1.0
S3_CSV ?= ml/data/raw/gym_members_exercise.csv
S4_CSV ?= ml/data/raw/bodyfat.csv

ml-deps: ## Поставить ML-зависимости (numpy/pandas/sklearn/lightgbm/joblib)
	$(call section,Устанавливаем ml-группу)
	@uv sync --group ml

ml-dataset: ## Сборка Dataset-B inbody_timeseries из Kaggle S3+S4
	$(call section,ETL Dataset-B)
	@test -f $(S3_CSV) || (echo "✗ $(S3_CSV) не найден; см. ml/data/processed/LICENSES.md"; exit 1)
	@test -f $(S4_CSV) || (echo "✗ $(S4_CSV) не найден; см. ml/data/processed/LICENSES.md"; exit 1)
	@uv run python -m ml.etl.inbody.cli --s3 $(S3_CSV) --s4 $(S4_CSV) --out ml/data/processed/

ml-train: ## Обучить все три модели (persistence + ridge + lgbm) и сравнить
	$(call section,Обучаем все модели)
	@uv run python -m ml.training.inbody_timeseries.persistence \
		--dataset $(ML_DATASET) --out-root $(ML_MODELS_ROOT) --version $(ML_VERSION)
	@uv run python -m ml.training.inbody_timeseries.train_ridge \
		--dataset $(ML_DATASET) --out-root $(ML_MODELS_ROOT) --version $(ML_VERSION)
	@uv run python -m ml.training.inbody_timeseries.train_lgbm \
		--dataset $(ML_DATASET) --out-root $(ML_MODELS_ROOT) --version $(ML_VERSION)
	@$(MAKE) ml-compare ML_VERSION=$(ML_VERSION) ML_MODELS_ROOT=$(ML_MODELS_ROOT)

ml-train-lgbm: ## Только основная модель LightGBM (быстрее, без сравнений)
	$(call section,LightGBM quantile)
	@uv run python -m ml.training.inbody_timeseries.train_lgbm \
		--dataset $(ML_DATASET) --out-root $(ML_MODELS_ROOT) --version $(ML_VERSION)

ml-compare: ## Сводная markdown-таблица метрик (для главы диплома)
	@uv run python -m ml.training.inbody_timeseries.compare \
		--root $(ML_MODELS_ROOT) --version $(ML_VERSION)

# --- ML #2: workout-recommender (spec 006, диплом Егора) ------------------

ML_REC_DATASET ?= ml/data/processed/dataset_c_workout_recommender.csv
ML_REC_MODELS_ROOT ?= ml/models/workout_rec
CATALOG ?= ml/data/processed/exercises_catalog.json

ml-rec-dataset: ## Сборка Dataset-C workout_recommender (rule-based labels)
	$(call section,ETL Dataset-C)
	@test -f $(S3_CSV) || (echo "✗ $(S3_CSV) не найден"; exit 1)
	@uv run python -m ml.etl.workout_recommender.cli \
		--s3 $(S3_CSV) $$(test -f $(S4_CSV) && echo "--s4 $(S4_CSV)") \
		--catalog $(CATALOG) --out ml/data/processed/

ml-rec-train: ## Обучить рекомендатор (popularity + LR + LGBM) и сравнить
	$(call section,Обучаем все модели рекомендатора)
	@uv run python -m ml.training.workout_recommender.popularity \
		--dataset $(ML_REC_DATASET) --out-root $(ML_REC_MODELS_ROOT) --version $(ML_VERSION)
	@uv run python -m ml.training.workout_recommender.train_lr \
		--dataset $(ML_REC_DATASET) --out-root $(ML_REC_MODELS_ROOT) --version $(ML_VERSION)
	@uv run python -m ml.training.workout_recommender.train_lgbm \
		--dataset $(ML_REC_DATASET) --out-root $(ML_REC_MODELS_ROOT) --version $(ML_VERSION)
	@$(MAKE) ml-rec-compare ML_VERSION=$(ML_VERSION) ML_REC_MODELS_ROOT=$(ML_REC_MODELS_ROOT)

ml-rec-compare: ## Сводная таблица метрик рекомендатора
	@uv run python -m ml.training.workout_recommender.compare \
		--root $(ML_REC_MODELS_ROOT) --version $(ML_VERSION)

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

# --- Production deploy ----------------------------------------------------
# Домен fitness-tracker.geox55.ru → 213.108.2.173.
# PWA собирается локально (флэттер уже стоит на dev-машине — `make pwa`),
# на сервер летит только готовый bundle + код. Подробности — deploy/README.md.

DEPLOY_HOST       ?= root@213.108.2.173
DEPLOY_PATH       ?= /opt/fitness-tracker
DEPLOY_API_URL    ?= https://fitness-tracker.geox55.ru/api/v1
DEPLOY_SSH_OPTS   ?= -o ServerAliveInterval=30

# Что НЕ синкаем на сервер. .env.prod уже на сервере и его НЕ перезаписываем;
# .git/.venv/кеши слишком тяжёлые и не нужны для прод-стека.
DEPLOY_RSYNC_EXCLUDES := \
	--exclude='.git/' \
	--exclude='.venv/' \
	--exclude='__pycache__/' \
	--exclude='*.pyc' \
	--exclude='.pytest_cache/' \
	--exclude='.mypy_cache/' \
	--exclude='.ruff_cache/' \
	--exclude='ml/data/raw/' \
	--exclude='ml/data/processed/' \
	--exclude='ml/data/interim/' \
	--exclude='ml/models/' \
	--exclude='ml/artifacts/' \
	--exclude='pwa/.dart_tool/' \
	--exclude='pwa/.pub-cache/' \
	--exclude='.env' \
	--exclude='.env.prod' \
	--exclude='.idea/' \
	--exclude='.vscode/' \
	--exclude='.claude/' \
	--exclude='*.log'

build-pwa: ## Собрать Flutter Web для прода (release-bundle с прод-URL API)
	$(call section,flutter build web --release)
	@cd pwa && flutter build web \
		--release \
		--base-href=/ \
		--dart-define=API_BASE_URL=$(DEPLOY_API_URL)
	@printf "\033[32m✓ PWA bundle: %s\033[0m\n" "$$(du -sh pwa/build/web | awk '{print $$1}')"

build-api: ## Собрать api-образ локально (linux/amd64) → fitness-tracker-api:latest
	$(call section,docker build api → fitness-tracker-api:latest)
	@docker build --platform linux/amd64 \
		-f deploy/api/Dockerfile \
		-t fitness-tracker-api:latest .
	@printf "\033[32m✓ api image: %s\033[0m\n" \
		"$$(docker image inspect fitness-tracker-api:latest --format '{{.Size}}' | awk '{printf \"%.0f MB\\n\", $$1/1024/1024}')"

deploy-sync: ## Только rsync кода на сервер (без сборки/перезапуска)
	$(call section,Rsync на $(DEPLOY_HOST):$(DEPLOY_PATH))
	@rsync -az --delete $(DEPLOY_RSYNC_EXCLUDES) \
		-e 'ssh $(DEPLOY_SSH_OPTS)' \
		./ $(DEPLOY_HOST):$(DEPLOY_PATH)/

deploy-image: build-api ## Передать локальный api-образ на сервер (save+load через ssh)
	$(call section,docker save api | ssh | docker load)
	@docker save fitness-tracker-api:latest \
		| gzip --fast \
		| ssh $(DEPLOY_SSH_OPTS) $(DEPLOY_HOST) 'gunzip | docker load'

deploy: build-pwa build-api deploy-sync deploy-image ## Полный деплой: build PWA/API локально → rsync + image → ssh deploy.sh
	$(call section,Запуск deploy.sh на сервере)
	@ssh $(DEPLOY_SSH_OPTS) $(DEPLOY_HOST) \
		'cd $(DEPLOY_PATH) && bash deploy/scripts/deploy.sh --skip-pull --skip-build-api'

deploy-logs: ## Хвост логов прод-стека (Ctrl+C для выхода)
	@ssh -t $(DEPLOY_SSH_OPTS) $(DEPLOY_HOST) \
		'cd $(DEPLOY_PATH) && docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f --tail=100'
