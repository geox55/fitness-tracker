# Security & GDPR

Свод решений по безопасности и требованиям GDPR. Привязка к спекам — везде, где есть исходное требование.

---

## Threat model (минимальная)

| Угроза | Вектор | Митигация |
|--------|--------|-----------|
| Перехват трафика | MITM | TLS на nginx, HSTS |
| Перебор паролей | brute force | Rate limit (5/10мин) + блок 15 мин (spec 001 REQ-06) |
| Утечка БД | SQL-инъекция, ошибки бэкапа | Параметризованные запросы (SQLAlchemy), encryption-at-rest для чувствительных полей |
| Утечка токенов | XSS, session hijack | HttpOnly + Secure для refresh; CSP; короткие TTL access |
| Несанкционированный доступ к чужим данным | broken access control | Проверка `user_id` в каждом сервисном слое; 404 (а не 403) |
| Раскрытие PII в логах | logging mistake | structlog filter; хеширование email, маскирование payloads |
| Утечка PDF/фото | прямой URL | Signed URLs, TTL ≤1 час |
| Утечка через ML | модель «помнит» данные | Анонимизация на ETL; PII не подаётся на инференс |
| LLM-провайдер видит данные | external dependency | Анонимизация промпта, feature flag, opt-in |
| Малисивный PDF | exploit парсера | Парсер в worker (sandbox), лимит 10 MB, не выполняем JS из PDF |
| GDPR violation | юридическое | Soft-delete + 30-day purge, экспорт данных, согласие при регистрации |

---

## Auth

### Хранение паролей

- **Алгоритм:** argon2id (parallelism=4, memory_cost=64MB, time_cost=3) через `passlib`.
- **Никогда** не логируем пароль; никогда не возвращаем хэш в API.

### JWT

| Тип | Где живёт | TTL |
|-----|-----------|-----|
| `access_token` | в памяти клиента (Riverpod state) | 15 минут |
| `refresh_token` | flutter_secure_storage (web → IndexedDB-protected) | 30 дней |

- Алгоритм: HS256, секрет в env (`JWT_SECRET`, 256 бит).
- В payload: `sub` (user_id), `iat`, `exp`, `type` (`access`/`refresh`), `jti` (для отзыва).
- Refresh-flow: при каждом refresh выдаётся новый refresh (rotation), старый помечается `used_at` в `auth_tokens`.
- При смене пароля → все refresh-токены пользователя помечаются `used_at`. Это инвалидирует все сессии.

### Rate limiting

- `POST /auth/login`: 5 неудач за 10 мин на пару `(IP, email)` → блок 15 мин (Redis INCR + TTL). См. spec 001 REQ-06.
- `POST /auth/forgot-password`: 3 запроса в час на email.
- Глобально: 60 RPS на IP (nginx).

### Восстановление пароля

- TTL токена восстановления — 1 час (spec 001 REQ-04).
- На запрос «забыли пароль» по несуществующему email отвечаем как при существующем (spec 001 NFR-04, timing-safe). Redis ключ ставится одинаково.
- Старые токены (>24ч) удаляются daily cron.

---

## Шифрование at-rest

### Что шифруется

| Данные | Метод | Где ключ |
|--------|-------|----------|
| Пароли пользователей | argon2id (one-way hash) | n/a |
| Refresh-tokens в БД | sha256(token) | n/a (хэшируем, не шифруем) |
| Чувствительные поля InBody (вес, % жира, мышечная масса, и т.д.) | Fernet (AES-128-CBC + HMAC) или libsodium secretbox, на уровне приложения | env `ENCRYPTION_KEY` (256 бит) |
| Email (опционально) | Fernet | env `ENCRYPTION_KEY` |
| PDF в MinIO | server-side encryption (SSE-S3) | MinIO master key |
| Фото профиля | server-side encryption (SSE-S3) | MinIO master key |

В Postgres шифрованные поля хранятся как `BYTEA` рядом с обычными колонками (например, `weight_kg_enc BYTEA` без plain `weight_kg`). Расшифровка в сервисном слое до отдачи клиенту/ml-inference.

> **Прагматичный fallback для MVP:** если сжимаются сроки диплома — допустимо ограничиться encryption-at-rest на уровне диска (volume encryption на хосте) + шифрование только refresh-tokens и oригинальных PDF. Зафиксировать это решение как «осознанное упрощение MVP» и разогнать в фазе 2.

### Ротация ключа

- Ключ `ENCRYPTION_KEY` хранится в env. Резервная копия — в LastPass/1Password команды.
- Ротация: вводим новый ключ как `ENCRYPTION_KEY_NEXT`, скрипт перешифровывает все BYTEA-поля, после чего `ENCRYPTION_KEY_NEXT` становится `ENCRYPTION_KEY`. В MVP не нужно — описание ради полноты.

---

## TLS

- Локально: self-signed через mkcert; в браузере — добавить корневой сертификат.
- На VPS: Let's Encrypt; HSTS заголовок `max-age=31536000; includeSubDomains; preload`.
- Версии TLS: 1.2 минимум, 1.3 предпочтительно. Запрещены SSLv3, TLS 1.0/1.1.

---

## Secrets management

| Где | Что |
|-----|-----|
| `.env` (gitignored) | DATABASE_URL, JWT_SECRET, ENCRYPTION_KEY, ML_INTERNAL_TOKEN, MINIO_*, SENDGRID_API_KEY, OPENAI_API_KEY |
| Репозиторий | `.env.example` с заглушками; никогда — реальные значения |
| CI | Repository secrets в GitHub Actions; passed как env при build/deploy |
| Бэкап секретов | password-manager команды |

Линт: pre-commit `gitleaks` — блокирует случайный коммит секретов.

---

## Headers и CSP

nginx добавляет:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

`'wasm-unsafe-eval'` нужен для Flutter Web (CanvasKit/Skia → WebAssembly). Если используется HTML-renderer, можно убрать.

---

## Авторизация

- Все ресурсы привязаны к `user_id`. Сервисный слой каждого домена явно проверяет: `where(user_id == current_user.id)`.
- Роли в MVP: только `user`. Для будущего admin-кабинета ввести `role` колонку в `users`.
- 404 (а не 403) на чужие ресурсы, чтобы не утечь информацию о их существовании.

---

## Внутренний канал api ↔ ml-inference

- `ml-inference` слушает на `:8001` только в docker-сети `internal`.
- nginx не проксирует `/internal/**`.
- Дополнительно — shared secret в заголовке `X-Internal-Token` (spec [01-system-components.md](01-system-components.md)).
- На уровне сети это уже «внутри», но secret-проверка защищает от шанса, что кто-то подключится к контейнеру через `docker exec` и сделает запрос обходным путём.

---

## Передача в LLM (если включён)

- **Feature flag** `LLM_ENABLED`. Если выключен — свободные вопросы в чате не уходят наружу.
- **Анонимизация промпта** перед отправкой:
  - Удаляются email, имя, точные даты рождения.
  - Используются только агрегированные характеристики: «мужчина 25-34, цель похудение, тренируется 4 раза в неделю».
- В ответе всегда добавляется disclaimer «Не медицинская рекомендация».
- Provider — OpenAI или альтернатива; ключ в env, никогда не в коде/логах.

---

## Парсер PDF

- Запускается в `worker` (отдельный процесс, не api).
- Лимит файла 10 MB.
- pdfplumber не выполняет встроенный JavaScript (мы и не должны).
- Если файл зашифрован паролем — не пробуем подбирать, возвращаем `encrypted` (spec 013 Scenario 5).
- Если файл — большой PDF с миллионами объектов (PDF bomb) — тайм-аут парсинга 30 секунд, OOM-protection на уровне docker memory limit.

---

## Доступ к файлам в MinIO

- Все объекты — private.
- Раздача только через **signed URL**: api генерирует URL с TTL 5 минут (для PDF InBody) или 1 час (для отчётов).
- TTL подтверждается в спеках: 003 NFR-04, 010 NFR-03.
- nginx не проксирует прямые URL MinIO — клиент идёт на signed URL напрямую (`minio` слушает только на внутреннем DNS, но в продакшене на VPS можно сделать публичный CNAME `files.fitness.example.com` → MinIO с TLS).

---

## GDPR

### Принципы

- **Минимизация данных:** собираем только то, что реально нужно для AI-блоков. Все поля профиля и InBody — обоснованы в спеках.
- **Явное согласие:** при регистрации — обязательный чекбокс «согласен с условиями и политикой конфиденциальности» (spec 001).
- **Право на доступ:** пользователь может скачать все свои данные одним JSON через `GET /api/v1/profile/export` (spec 002 NFR-03).
- **Право на удаление:** через `DELETE /api/v1/auth/account` → soft-delete, через 30 дней — hard purge (spec 001 REQ-11, 002).
- **Право на исправление:** профиль редактируется (spec 002), InBody-замеры — удаляются и создаются заново (spec 003).

### Soft-delete и purge

```mermaid
flowchart LR
    a[Пользователь<br/>DELETE /auth/account] --> b[users.deleted_at = now()]
    b --> c{30 дней}
    c -->|истекли| d[GDPR purge cron]
    d --> e[CASCADE delete users<br/>(всё связанное удаляется)]
    d --> f[MinIO: rm -rf user_id/*]
    c -->|пользователь передумал| g[не реализовано в MVP]
```

В MVP «передумать в течение 30 дней» — out of scope.

### Покрытие удаления

При удалении пользователя удаляются (через CASCADE):
- user_profiles
- notification_preferences
- auth_tokens
- inbody_measurements + pdf_import_jobs
- workouts + exercise_logs
- workout_plans + plan_weeks + plan_days + plan_exercises
- nutrition_plans + nutrition_days + meals
- inbody_forecasts + forecast_evaluations
- plan_rebuild_events
- chat_messages
- notification_outbox

В MinIO purge-скрипт удаляет все объекты с префиксом `{user_id}/` во всех бакетах.

### Обучающие данные

- Анонимизированные training data (spec 012 REQ-17): `user_id` хэширован, даты сдвинуты.
- При удалении пользователя его след в обучающих датасетах не удаляется автоматически — это анонимизированные агрегаты, ссылка на конкретного человека невозможна. Это документируется в политике конфиденциальности.

### Логи

- В логах email — только хэш или маска (`u***@gmail.com`).
- IP, User-Agent — записываются для аудита auth-событий, retention 90 дней, потом truncate.
- Stack traces могут содержать данные — фильтр в structlog убирает поля по списку (`password`, `token`, `email`, ...).

---

## Аудит-журнал

Минимально: пишем в отдельную таблицу `audit_log` важные события:
- регистрация
- логин (успех/неудача)
- смена пароля
- удаление аккаунта
- автоматическая регенерация плана
- отправка GDPR-экспорта

В MVP — простая таблица с `(user_id, event_type, created_at, details JSONB)`. Retention 1 год.

---

## Ответственное раскрытие

- Email команды (security.contact в README) для приёма репортов уязвимостей.
- В MVP — без bug bounty.

---

## Compliance чек-лист (для защиты диплома)

- [ ] HTTPS на всём периметре с современным ciphersuite
- [ ] Хэширование паролей argon2id
- [ ] Rate-limit на auth-эндпоинтах
- [ ] JWT с короткими TTL и rotation
- [ ] Шифрование sensitive полей в БД (даже если упрощённо)
- [ ] Signed URLs для object storage
- [ ] CSP, HSTS, X-Frame-Options заголовки
- [ ] Анонимизация в training data
- [ ] Soft-delete + 30-day purge для GDPR
- [ ] Экспорт данных пользователя одним JSON
- [ ] Согласие на обработку данных при регистрации
- [ ] Описание политики конфиденциальности (отдельный документ, юридический текст вне scope команды)
- [ ] LLM (если используется) — feature-flag + анонимизация промпта
- [ ] Pre-commit gitleaks для секретов
