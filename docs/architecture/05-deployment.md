# Deployment — docker-compose

Целевая среда — локальный docker-compose, легко переносится на одиночный VPS.

---

## Топология

```mermaid
flowchart TB
    subgraph host["docker-compose host"]
        nginx["nginx :443/:80"]
        pwa_static["pwa volume<br/>(статика Flutter Web)"]
        api["api :8000"]
        ml["ml-inference :8001"]
        worker["worker"]
        beat["beat"]
        pg[("postgres :5432<br/>volume: pgdata")]
        redis[("redis :6379<br/>volume: redisdata")]
        minio[("minio :9000<br/>volume: miniodata")]
        nginx -. internal .-> api
        nginx -. internal .-> pwa_static
        api -. internal .-> ml
        api -. internal .-> pg
        api -. internal .-> redis
        api -. internal .-> minio
        worker -. internal .-> pg
        worker -. internal .-> redis
        worker -. internal .-> minio
        worker -. internal .-> ml
        beat -. internal .-> redis
        ml -. internal .-> pg
    end

    user(("Пользователь<br/>браузер")) -- HTTPS :443 --> nginx
    user -- HTTP :80 → redirect --> nginx
```

Все сервисы — в одной docker-сети `internal`. Наружу торчит только nginx (порты 80/443).

---

## docker-compose.yml (структура)

```yaml
name: fitness-tracker

services:
  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deploy/nginx/certs:/etc/nginx/certs:ro
      - pwa_build:/usr/share/nginx/html:ro
    depends_on:
      api: { condition: service_healthy }
    networks: [internal]
    restart: unless-stopped

  pwa_builder:
    # одноразовый сервис: собирает Flutter Web в volume pwa_build
    build: ./pwa
    volumes:
      - pwa_build:/output
    profiles: [build]

  api:
    build: { context: ., dockerfile: deploy/api/Dockerfile }
    environment:
      DATABASE_URL: postgresql+asyncpg://app:${POSTGRES_PASSWORD}@postgres:5432/fitness
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: http://minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      ML_INTERNAL_URL: http://ml-inference:8001
      ML_INTERNAL_TOKEN: ${ML_INTERNAL_TOKEN}
      JWT_SECRET: ${JWT_SECRET}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
      LLM_ENABLED: "${LLM_ENABLED:-false}"
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      ENV: production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 10s
      timeout: 3s
      retries: 5
    depends_on:
      postgres: { condition: service_healthy }
      redis:    { condition: service_healthy }
      minio:    { condition: service_healthy }
      ml-inference: { condition: service_healthy }
    networks: [internal]
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: "1.5", memory: 1024M }

  ml-inference:
    build: { context: ., dockerfile: deploy/ml-inference/Dockerfile }
    environment:
      WORKOUT_GEN_VERSION: "0.3.1"
      INBODY_PRED_VERSION: "0.4.2"
      ML_INTERNAL_TOKEN: ${ML_INTERNAL_TOKEN}
      MODELS_DIR: /models
    volumes:
      - ./ml/models:/models:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/internal/v1/health"]
      interval: 15s
      timeout: 3s
      retries: 5
    networks: [internal]
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: "2", memory: 2048M }

  worker:
    build: { context: ., dockerfile: deploy/api/Dockerfile }
    command: celery -A app.celery_app worker -l INFO -Q default,pdf,email,watchers,ml
    environment: # тот же набор, что и api
      <<: *api_env
    depends_on:
      api: { condition: service_healthy }
    networks: [internal]
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: "2", memory: 1536M }

  beat:
    build: { context: ., dockerfile: deploy/api/Dockerfile }
    command: celery -A app.celery_app beat -l INFO --schedule=/data/celerybeat-schedule
    environment:
      <<: *api_env
    volumes:
      - beat_data:/data
    depends_on:
      redis: { condition: service_healthy }
    networks: [internal]
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: fitness
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./deploy/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d fitness"]
      interval: 5s
      timeout: 3s
      retries: 10
    networks: [internal]
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
    networks: [internal]
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    command: server /data --console-address :9001
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - miniodata:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks: [internal]
    # консоль MinIO (9001) не публикуется наружу; доступ только через docker exec/internal
    restart: unless-stopped

  minio_init:
    image: minio/mc:latest
    depends_on: { minio: { condition: service_healthy } }
    entrypoint: >
      /bin/sh -c "
        mc alias set local http://minio:9000 $$MINIO_ACCESS_KEY $$MINIO_SECRET_KEY;
        mc mb -p local/inbody-pdf-temp local/inbody-pdf local/profile-photos local/analytics-reports || true;
        mc ilm import local/inbody-pdf-temp < /policies/temp-ttl.json;
      "
    environment:
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
    volumes:
      - ./deploy/minio/policies:/policies:ro
    networks: [internal]
    profiles: [init]

volumes:
  pgdata:
  redisdata:
  miniodata:
  pwa_build:
  beat_data:

networks:
  internal:
    driver: bridge
```

> Прим.: `*api_env` — YAML anchor; в реальном файле раскрывается через `x-api-env: &api_env`.

---

## Профили docker-compose

| Профиль | Команды |
|---------|---------|
| (default) | `docker compose up` — все долгоживущие сервисы |
| `build` | `docker compose --profile build run --rm pwa_builder` — сборка Flutter Web |
| `init` | `docker compose --profile init up minio_init` — создание бакетов и lifecycle policies |

---

## Переменные окружения

`.env.example` (коммитится; реальный `.env` — нет):

```dotenv
# Postgres
POSTGRES_PASSWORD=changeme

# MinIO
MINIO_ACCESS_KEY=fitness-app
MINIO_SECRET_KEY=changeme

# JWT (ключ для подписи)
JWT_SECRET=base64-32-bytes-here

# Шифрование чувствительных полей в БД
ENCRYPTION_KEY=base64-32-bytes-here

# Внутренний токен для ml-inference
ML_INTERNAL_TOKEN=base64-32-bytes-here

# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxx

# LLM
LLM_ENABLED=false
OPENAI_API_KEY=

# ML model versions
WORKOUT_GEN_VERSION=0.3.1
INBODY_PRED_VERSION=0.4.2
```

Генерация ключей:
```bash
openssl rand -base64 32
```

---

## nginx конфиг (контур)

```nginx
events {}

http {
    upstream api { server api:8000; }

    # rate limit для auth-эндпоинтов (см. spec 001 REQ-06)
    limit_req_zone $binary_remote_addr zone=auth_zone:10m rate=10r/m;

    server {
        listen 80;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name fitness.local;
        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        gzip on;
        gzip_types text/plain text/css application/json application/javascript;

        # PWA статика
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;   # SPA-роутинг
        }

        location /api/v1/auth/ {
            limit_req zone=auth_zone burst=5 nodelay;
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/v1/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 60s;
        }

        # /internal/** не проксируется — заведомо отсутствует
        location /internal/ { return 404; }
    }
}
```

TLS:
- Локально: self-signed через `mkcert` или `openssl`.
- На VPS: Let's Encrypt через certbot или `nginx-proxy + acme-companion`.

---

## Инициализация и первый запуск

```bash
# 1. Сборка PWA-статики (раз в релиз)
docker compose --profile build run --rm pwa_builder

# 2. Поднять долгоживущие сервисы
docker compose up -d postgres redis minio

# 3. Создать бакеты MinIO
docker compose --profile init up minio_init

# 4. Применить миграции (одноразовый run)
docker compose run --rm api alembic upgrade head

# 5. Сидинг каталога упражнений (см. spec 012)
docker compose run --rm api python -m ml.seed.seed_exercises \
  --in /app/ml/data/processed/dataset_a_exercises.parquet

# 6. Старт остальных сервисов
docker compose up -d

# Проверка
curl -k https://fitness.local/api/v1/health
```

---

## Запуск ML-обучения

Обучение происходит вне docker-compose (или в отдельном one-shot контейнере). Артефакты копируются в `ml/models/`, версия пина́ется через env, и `ml-inference` рестартится:

```bash
# Локально (через uv)
uv run python -m ml.training.train_workout_gen \
  --data ml/data/processed/dataset_b_workout_recsys.parquet \
  --out ml/models/workout_gen-0.4.0 --seed 42

# Обновляем версию в .env
sed -i '' 's/WORKOUT_GEN_VERSION=.*/WORKOUT_GEN_VERSION=0.4.0/' .env

# Рестартим ml-inference
docker compose up -d --force-recreate ml-inference
```

---

## Бэкапы

Минимальный набор для VPS:

```bash
# Postgres dump (cron daily)
docker compose exec -T postgres pg_dump -U app fitness | gzip > backups/fitness-$(date +%F).sql.gz

# MinIO bucket sync (cron weekly)
docker compose exec mc mc mirror local/inbody-pdf /backup/minio/inbody-pdf
```

Для локалки бэкапы не обязательны.

---

## Health-чеки и деплой-проверка

```bash
# Все контейнеры healthy?
docker compose ps

# API
curl -k https://fitness.local/api/v1/health
# → {"status":"ok","version":"...","db":"ok","redis":"ok","minio":"ok"}

# ML
docker compose exec api curl -s -H "X-Internal-Token: $ML_INTERNAL_TOKEN" \
  http://ml-inference:8001/internal/v1/health
# → {"status":"ok","models":{"workout_gen":"0.3.1","inbody_pred":"0.4.2"}}

# Celery
docker compose exec worker celery -A app.celery_app inspect ping
```

---

## Логи

- `docker compose logs -f api worker beat ml-inference`
- Все сервисы пишут JSON-структурированные логи в stdout.
- Trace ID `X-Request-ID` пробрасывается через все вызовы (api → ml → worker через `task_headers`).

---

## Resource budget (для презентации диплома)

| Сервис | CPU | Memory |
|--------|-----|--------|
| nginx | 0.2 | 64 MB |
| api | 1.5 | 1024 MB |
| ml-inference | 2.0 | 2048 MB |
| worker | 2.0 | 1536 MB |
| beat | 0.1 | 128 MB |
| postgres | 1.0 | 512 MB |
| redis | 0.3 | 128 MB |
| minio | 0.5 | 512 MB |
| **Total** | ~7.6 cores | ~6 GB RAM |

Должно укладываться на ноут или VPS 8 vCPU / 8 GB.

---

## CI/CD (минимально)

```mermaid
flowchart LR
    push[git push] --> ci[GitHub Actions]
    ci --> lint[ruff + mypy]
    ci --> tests[pytest]
    ci --> migrations[alembic check]
    ci --> flutter[flutter analyze + test]
    ci --> build[docker build api+ml]
```

Деплой на VPS — вручную через `git pull && docker compose up -d --build` или через GitHub Action с SSH-runner. Для диплома — вручную достаточно.
