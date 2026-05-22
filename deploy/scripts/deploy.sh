#!/usr/bin/env bash
# Деплой fitness-tracker на прод-сервер.
# Запускать на сервере из корня репозитория (/opt/fitness-tracker по умолчанию).
#
# Что делает:
#   1. git pull --ff-only (если репо git'овое; иначе пропуск — код кладёт rsync).
#   2. Проверка, что PWA-bundle (pwa/build/web/index.html) есть. Сборка PWA —
#      локальная на dev-машине (см. make build-pwa), сервер её НЕ собирает.
#   3. Билд образов api / angie с --pull.
#   4. docker compose up -d (api-migrate отработает миграции, angie подхватит
#      статику из bind-mount ./pwa/build/web и сам выпустит/обновит cert).
#   5. Сидинг exercise-catalog (опционально).
#   6. Smoke-тест /api/v1/health (по HTTPS — попутно проверяем, что Angie
#      получил сертификат у Let's Encrypt; на первом запуске может занять
#      до ~60 секунд).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

ENV_FILE="${ENV_FILE:-.env.prod}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
COMPOSE=( docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" )

SKIP_PULL=0
SKIP_SEED=0
SKIP_BUILD_API=0
for arg in "$@"; do
    case "$arg" in
        --skip-pull) SKIP_PULL=1 ;;
        --skip-seed) SKIP_SEED=1 ;;
        --skip-build-api) SKIP_BUILD_API=1 ;;
        -h|--help)
            cat <<EOF
Usage: deploy.sh [--skip-pull] [--skip-seed] [--skip-build-api]

  --skip-pull       Не делать git pull (полезно при rsync-репо).
  --skip-seed       Пропустить сидинг exercise catalog.
  --skip-build-api  Не пересобирать api-образ (используется make deploy:
                    образ грузится локально через docker save | docker load).

Переменные окружения:
  ENV_FILE       (default: .env.prod)
  COMPOSE_FILE   (default: docker-compose.prod.yml)
EOF
            exit 0
            ;;
        *) echo "Неизвестный флаг: $arg" >&2; exit 1 ;;
    esac
done

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: $ENV_FILE не найден. Создайте его на основе .env.prod.example." >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

DOMAIN="${DOMAIN:-portal.geox55.ru}"
HEALTH_URL="${HEALTH_URL:-https://$DOMAIN/api/v1/health}"

# ---------- 1. git pull (опционально) ---------------------------------------
# На сервере мы сейчас держим репо как rsync-копию без .git — в этом случае
# pull тихо пропускается. Если ты переедешь на git-clone-вариант, всё
# заработает как было.
if [[ "$SKIP_PULL" -eq 0 ]] && git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "▶ 1/5 git pull --ff-only"
    git -C "$REPO_ROOT" pull --ff-only
elif [[ "$SKIP_PULL" -eq 0 ]]; then
    echo "▶ 1/5 git pull пропущен ($REPO_ROOT — не git-репо, синхронизация через rsync)"
else
    echo "▶ 1/5 git pull пропущен (--skip-pull)"
fi

# ---------- 2. Проверяем готовый PWA-bundle ---------------------------------
PWA_DIR="$REPO_ROOT/pwa/build/web"
if [[ ! -f "$PWA_DIR/index.html" ]]; then
    echo "✗ Не найден $PWA_DIR/index.html." >&2
    echo "  Соберите локально: make build-pwa и повторите make deploy." >&2
    exit 1
fi
echo "▶ 2/6 PWA bundle найден ($(du -sh "$PWA_DIR" | awk '{print $1}'))."

# ---------- 3. Билд образов -------------------------------------------------
# angie собирается всегда (instant, ~10KB конфиг + alpine base).
# api — только если запускают `deploy.sh` отдельно (без `make deploy`),
# который сам пришлёт готовый образ через docker save | docker load.
if [[ "$SKIP_BUILD_API" -eq 0 ]]; then
    if ! docker image inspect fitness-tracker-api:latest >/dev/null 2>&1; then
        echo "▶ 3/6 Билдим образы (angie + api)…"
        "${COMPOSE[@]}" build --pull angie api
    else
        echo "▶ 3/6 api-образ уже есть, билдим только angie…"
        "${COMPOSE[@]}" build --pull angie
    fi
else
    echo "▶ 3/6 --skip-build-api: api-образ ожидается готовым; билдим только angie…"
    "${COMPOSE[@]}" build --pull angie
fi

# ---------- 4. Up -----------------------------------------------------------
echo "▶ 4/6 docker compose up -d --remove-orphans"
"${COMPOSE[@]}" up -d --remove-orphans

# Дадим api-migrate время отработать (он завершится сам, но логи покажут
# применённые ревизии — полезно в выводе деплоя).
sleep 2
echo "  Последние логи api-migrate:"
"${COMPOSE[@]}" logs --no-color --tail=20 api-migrate || true

# ---------- 4. Сидинг exercise-catalog (опционально) -----------------------
# Каталог упражнений хранится в ml/data/processed/exercises_catalog.json,
# который генерируется ETL-пайплайном (см. make ml-rec-dataset). На свежем
# сервере его обычно нет — тогда seed пропускается без ошибки.
SEED_CATALOG="${SEED_CATALOG:-ml/data/processed/exercises_catalog.json}"
if [[ "$SKIP_SEED" -eq 0 ]] && [[ -f "$SEED_CATALOG" ]]; then
    echo "▶ 5/6 Ждём пока api примет exec…"
    for _ in $(seq 1 90); do
        if "${COMPOSE[@]}" exec -T api python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health').read()" >/dev/null 2>&1; then
            echo "  ✓ api отвечает на /health изнутри контейнера"
            break
        fi
        sleep 2
    done

    echo "  Сидим exercise catalog из $SEED_CATALOG…"
    "${COMPOSE[@]}" exec -T api python -m app.scripts.seed_exercises "$SEED_CATALOG"
elif [[ "$SKIP_SEED" -eq 0 ]]; then
    echo "▶ 5/6 Сидинг пропущен: нет $SEED_CATALOG (сгенерируйте через make ml-rec-dataset)"
else
    echo "▶ 5/6 Сидинг пропущен (--skip-seed)"
fi

# ---------- 6. Smoke-тест ---------------------------------------------------
# По HTTPS — попутно валидируем, что Angie успешно получил/обновил
# Let's Encrypt cert. На холодном volume angie_acme первый выпуск
# занимает 15-60 секунд (один HTTP-01 round-trip к LE + сохранение).
echo "▶ 6/6 Smoke-тест $HEALTH_URL"
for _ in $(seq 1 60); do
    if curl -fsS "$HEALTH_URL" >/dev/null; then
        echo "  ✓ API готов (TLS-серт получен, https отвечает)"
        exit 0
    fi
    sleep 2
done
echo "✗ API не ответил по HTTPS за ~120 секунд" >&2
"${COMPOSE[@]}" ps
echo "--- angie ACME logs ---" >&2
"${COMPOSE[@]}" logs --no-color --tail=40 angie | grep -iE "acme|cert|ssl" >&2 || true
echo "--- api logs ---" >&2
"${COMPOSE[@]}" logs --no-color --tail=80 api
exit 1
