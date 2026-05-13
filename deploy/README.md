# Production-развёртывание fitness-tracker

Стек поднимается одной командой `make deploy` с dev-машины. Домен —
`fitness-tracker.geox55.ru` (A-запись на `213.108.2.173`). Фронт
(Flutter Web) и API (FastAPI) живут на одном origin, MinIO спрятан
за `/s3/`-префиксом, TLS — Let's Encrypt через **встроенный ACME-модуль
Angie**. Никакого host-certbot, systemd-таймеров и хуков на reload
больше нет — Angie сам ходит в LE по HTTP-01 и без рестарта перезаряжает
ssl-контекст.

## Архитектура (кратко)

```
Browser ──HTTPS:443──▶ angie ──▶ /              (Flutter Web static)
                            ├──▶ /api/*         (FastAPI :8000)
                            └──▶ /s3/*          (MinIO :9000, signed URLs)
                              │
                              └──▶ HTTP-01 :80 ──▶ Let's Encrypt
                                       │
                                       │ persists in named volume
                                       ▼
                                 angie_acme
                                 (account.key + certificate.pem)
```

Внутри docker-сети `internal` — postgres, api, api-migrate, api-cleanup,
minio, minio-init. Наружу выставлены только 80/443.

## Первый деплой

### 1. DNS

```bash
dig +short fitness-tracker.geox55.ru
# Должен ответить 213.108.2.173
```

Если запись ещё не создана — добавить A-запись у регистратора geox55.ru:

```
fitness-tracker  A  213.108.2.173  TTL=300
```

Подождать пока DNS прорастёт (`dig` снаружи; 5–30 минут). Это критично:
без рабочего DNS Let's Encrypt не сможет верифицировать HTTP-01.

### 2. Подготовка сервера

```bash
ssh root@213.108.2.173

# Базовый софт. certbot НЕ нужен — ACME встроен в Angie.
apt update
apt install -y docker.io docker-compose-plugin git curl ufw openssl

# Firewall (важно: 22 — наш ssh, 80/443 — public, остальное закрыто).
# Порт 80 нужен Angie для HTTP-01 challenge.
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Каталог под проект
mkdir -p /opt/fitness-tracker
```

### 3. Секреты

С dev-машины — `make deploy-sync` положит код в `/opt/fitness-tracker`,
после чего на сервере:

```bash
ssh root@213.108.2.173
cd /opt/fitness-tracker
cp .env.prod.example .env.prod
chmod 600 .env.prod
```

Сгенерировать три сильных секрета и подставить их в `.env.prod`:

```bash
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)"
echo "JWT_SECRET=$(openssl rand -base64 32)"
echo "S3_SECRET_KEY=$(openssl rand -base64 32)"
```

Не забыть синхронно обновить `POSTGRES_PASSWORD` и пароль внутри
`DATABASE_URL` (одно и то же значение).

`CORS_ORIGINS` обязательно держать в **single-quotes** (docker compose
v2.5+ срезает голые double-quotes из `.env`, и pydantic потом не парсит
JSON-массив — см. соответствующий комментарий в `docker-compose.prod.yml`).

### 4. TLS — ничего настраивать не нужно

Angie сам выпустит сертификат на первом старте. Параметры — в
[`deploy/angie/angie.prod.conf`](angie/angie.prod.conf):

```nginx
acme_client letsencrypt https://acme-v02.api.letsencrypt.org/directory
    email=admin@geox55.ru
    renew_before_expiry=30d;
```

Проверить выпуск после первого деплоя:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod \
    logs angie 2>&1 | grep -iE "acme|certificate"
```

Должно быть `account registered` и `certificate obtained`. Обновляется
автоматически за 30 дней до истечения, без перезагрузки контейнера.

### 5. Деплой всего стека

С dev-машины:

```bash
make deploy
```

`make deploy` делает четыре шага:

1. `make build-pwa` — `flutter build web --release` локально,
   `API_BASE_URL` подставляется как `https://fitness-tracker.geox55.ru/api/v1`.
2. `make build-api` — `docker build` для api на dev-машине (linux/amd64).
3. `make deploy-sync` + `make deploy-image` — `rsync` репо + `docker save | ssh | docker load`
   образа api на сервер (`.env.prod` не трогается, тяжёлые кеши исключены).
4. `ssh ... deploy.sh --skip-pull --skip-build-api` — на сервере собирается
   только `angie` (api/nginx уже готовые), `api-migrate` применяет миграции,
   `angie` стартует, выпускает cert и проксирует трафик.

Если нужно только пересинхронизировать код без перезапуска:
`make deploy-sync`. Если нужно только перекатить api без PWA:
`make build-api deploy-image && ssh root@... 'cd /opt/fitness-tracker && docker compose -f docker-compose.prod.yml --env-file .env.prod up -d api'`.

### 6. Smoke-тест

```bash
curl -I https://fitness-tracker.geox55.ru/                # 200, text/html
curl https://fitness-tracker.geox55.ru/api/v1/health      # {"status":"ok"}
```

Открыть в браузере — должна загрузиться PWA, проверить регистрацию
тестового пользователя.

## Обновление кода

С dev-машины одной командой:

```bash
make deploy
```

Это `flutter build web` → `docker build api` → `rsync` + `docker save/load` →
`ssh deploy.sh`. Pull не делается, потому что код на сервере хранится
rsync'ом (а не git-clone'ом).

## Полезное

- **Логи всех сервисов**:
  `docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f --tail=100`
- **Только api**:
  `docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f api`
- **ACME-логи Angie**:
  `docker compose ... logs angie 2>&1 | grep -i acme`
- **psql внутрь Postgres**:
  `docker compose -f docker-compose.prod.yml --env-file .env.prod exec postgres psql -U app -d fitness`
- **MinIO web-console** (только через ssh-туннель, не публично):
  `ssh -L 9001:172.17.0.1:9001 root@213.108.2.173`
- **Бэкап Postgres**:
  `docker compose ... exec -T postgres pg_dump -U app fitness | gzip > backup-$(date +%F).sql.gz`
- **Принудительный re-issue cert** (например, после смены домена в
  `angie.prod.conf`): `docker compose ... exec angie rm -rf /var/lib/angie/acme/letsencrypt && docker compose ... restart angie`.

## Известные ограничения

- `email_verification_required=False` — регистрация без подтверждения.
  При подключении реального SMTP включить флаг в `.env.prod`.
- Flutter Web bundle собирается **локально** через `make build-pwa`
  (~10–60 секунд на инкрементальный билд, ~75 секунд на чистый). Сервер
  Flutter SDK не держит — экономия диска и времени.
- api-образ тоже собирается **локально** через `make build-api` и едет
  на сервер `docker save | gzip | ssh | docker load` (~80-150 MB после gzip).
- PWA доставляется rsync'ом в `pwa/build/web/` и монтируется в angie
  bind-mount'ом, поэтому новый билд видно сразу без перестарта (только
  хеши имён файлов меняются — клиент сам подтянет свежие).
- ACME-state живёт в named volume `angie_acme`. Удаление volume = новый
  запрос в Let's Encrypt: rate-limit 5 запросов/домен/неделю, в проде
  это ничего не ломает, но без нужды трогать не стоит.
- При первом запуске после `compose down -v` или на свежем сервере
  Angie ~30-60 секунд не отдаёт HTTPS (пока идёт HTTP-01 round-trip).
  В этот момент HTTP-redirect на 80 продолжает работать.
