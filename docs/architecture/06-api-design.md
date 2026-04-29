# API Design

Конвенции, общие для всех публичных эндпоинтов FastAPI. Конкретные ручки описаны в спеках 001–013.

---

## Базовые правила

### Версионирование

- URL-path версия: `/api/v1/...`. Внутренние эндпоинты ml-inference: `/internal/v1/...`.
- Mажорная версия меняется только при breaking-changes контракта (никогда — для добавления полей/эндпоинтов).
- В `OpenAPI` schema указывается `version: 1.0.0` + bump при изменениях.

### Naming

- URI — `kebab-case`, существительные множественного числа: `/inbody/measurements`, `/workouts`.
- JSON-поля — `snake_case` (на всех слоях, включая клиента).
- Action endpoints используют POST на под-ресурсе глаголом: `POST /workouts/{id}/finish`, не `POST /finish-workout`.

### HTTP-методы

| Метод | Использование |
|-------|---------------|
| GET | Чтение, идемпотентно, без побочных эффектов |
| POST | Создание ресурса; вызов действия (`finish`, `generate`) |
| PATCH | Частичное обновление (preferred over PUT) |
| PUT | Полное замещение (используем редко — только в файловых эндпоинтах) |
| DELETE | Удаление |

### Идемпотентность

- GET, PUT, DELETE — всегда идемпотентны.
- POST на «создание» — допускает поддержку `Idempotency-Key` (заголовок) для долгоиграющих создающих ручек (генерация плана, экспорт PDF). В MVP — опционально.
- POST на «действия» (finish, cancel, archive) — идемпотентны на уровне домена (повторный вызов на уже завершённой тренировке возвращает 409 conflict с текущим состоянием).

### Аутентификация

- Все эндпоинты, кроме `/auth/register`, `/auth/login`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/verify-email`, `/health`, требуют `Authorization: Bearer <access_token>`.
- Внутренние (`/internal/v1/**`) — `X-Internal-Token: <ml_internal_token>`. nginx не проксирует их наружу.

### Авторизация

- Любой ресурс, привязанный к `user_id`, доступен только своему пользователю. Проверка — в каждом сервисном слое (не на уровне роутера). Если ресурс не принадлежит текущему пользователю — 404 (не 403, чтобы не утечь информацию о существовании ресурса).

### Pagination

Курсорная пагинация для списков большого размера; offset-based для коротких:

```
GET /api/v1/workouts?limit=20&offset=0
```
Response:
```json
{
  "items": [...],
  "total": 142,
  "limit": 20,
  "offset": 0
}
```

Для длинных лент (notifications inbox, chat) — курсорная:
```
GET /api/v1/chat/messages?limit=50&before=2026-04-28T00:00:00Z
```

### Sorting & filtering

- Сортировка по умолчанию указывается в спеке (обычно по `created_at DESC` или domain-specific полю).
- Фильтры — query-параметры, multi-value через запятую: `?muscle_group=chest,back`.

### Дата/время

- Все даты-времена — ISO 8601 в UTC с явным `Z`: `2026-04-28T12:00:00Z`.
- Только-даты (`birth_date`, `valid_until`) — `YYYY-MM-DD`.
- Сервер всегда отдаёт UTC; клиент конвертирует в локальную TZ при отображении.

### Числа

- Денежные значения и единицы — числа JSON (не строки).
- Проценты как числа с плавающей точкой (например, `body_fat_percent: 18.2`), не строки `"18.2%"`.
- Граммы и калории — целые числа (Integer); веса в кг — десятичные с двумя знаками.

### Размер тел запроса/ответа

- Запросы JSON — лимит 1 MB; multipart для файлов — 10 MB (PDF) / 5 MB (фото).
- Ответы — без жёсткого лимита, но списки всегда пагинируются.

---

## Структура успешного ответа

```json
{
  "id": "uuid",
  "field_a": "value",
  "nested": {
    "x": 1
  }
}
```

Без обёртки `data: {...}`, чтобы не плодить уровни. Списки:
```json
{
  "items": [...],
  "total": N
}
```

Async-операции:
```json
{ "job_id": "uuid", "status": "queued" }
```

---

## Структура ошибок

Единый формат:

```json
{
  "error": "machine_readable_code",
  "message": "Человекочитаемое описание для UI",
  "details": { /* опционально, контекст */ }
}
```

| HTTP | Когда |
|------|-------|
| 400 | Невалидное тело/параметры (`bad_request`, `weak_password`, `incomplete_profile`) |
| 401 | Отсутствует/невалидный токен (`invalid_credentials`, `token_expired`) |
| 403 | Аутентифицирован, но не разрешено (`email_unconfirmed`) |
| 404 | Ресурс не найден / не доступен текущему пользователю |
| 409 | Конфликт состояний (`workout_not_in_progress`, `email_taken`) |
| 410 | Токен использован/истёк (`token_used`) |
| 413 | Файл слишком большой |
| 415 | Неподдерживаемый Content-Type |
| 422 | Pydantic validation error (формат от FastAPI, `error: "validation_error"`) |
| 429 | Rate limit (с заголовком `Retry-After`) |
| 500 | Серверная ошибка — общий `internal_error` |
| 503 | Внешний сервис недоступен (ml-inference timeout, SendGrid down) |
| 504 | Long-running ml-inference timeout |

Pydantic 422 переопределяется глобальным exception handler-ом, чтобы соответствовать формату выше:

```json
{
  "error": "validation_error",
  "message": "Не удалось обработать запрос",
  "details": [
    { "field": "password", "issue": "min_length", "limit": 8 }
  ]
}
```

---

## Async-operations pattern

Все операции, которые могут идти >2 секунд:
- Генерация плана тренировок (spec 006)
- Парсинг PDF InBody (spec 013)
- Экспорт PDF-отчёта (spec 010)
- Прогноз InBody (spec 008) — обычно быстрый, но защищён через таймаут
- (Опц.) Генерация меню питания через LLM (spec 007)

Pattern:

```
POST /api/v1/<resource>/<action>      → 202 { job_id, status: "queued" }
GET  /api/v1/<resource>/<action>/{job_id}  → 200 { status, result | progress }
```

Когда возможно (например, генерация плана), сервер делает синхронно — отвечает `201 + результат`. Async-канал только для тяжёлых.

---

## Заголовки

### Запрос

| Заголовок | Назначение |
|-----------|------------|
| `Authorization: Bearer ...` | JWT access |
| `Idempotency-Key: ...` | (опц.) для защиты от двойного создания |
| `X-Request-ID: ...` | (опц.) клиентский trace id; иначе генерируется сервером |
| `Accept-Language: ru,en` | (фаза 2) локализация |

### Ответ

| Заголовок | Назначение |
|-----------|------------|
| `X-Request-ID` | trace id (всегда) |
| `Retry-After` | при 429/503 |
| `Cache-Control: private, max-age=60` | для read-эндпоинтов |
| `ETag` | (опц.) для conditional GET |

---

## Rate limiting

| Что | Лимит | Где |
|-----|-------|-----|
| `POST /auth/login` | 5 неудач за 10 мин на IP+email → блок 15 мин | spec 001 REQ-06 |
| Любой `POST /chat/messages` | 30 сообщений/час на пользователя | spec 009 |
| Любой `POST /inbody/.../from-pdf` | 10 загрузок в день на пользователя | spec 013 |
| Дефолт | 60 RPS на IP | nginx |

Реализация: nginx limit_req для глобального; Redis (`INCR ... EX`) для per-user.

---

## Versioning контрактов

- В `OpenAPI` каждая ручка имеет `tags: [<domain>]`, `summary`, `description`.
- Удаление полей или ручек требует deprecation цикла: пометить `deprecated: true`, держать ≥1 минор-версию.
- Добавление полей в request — только optional (default values).
- Добавление полей в response — допустимо без version-bump (клиент не должен ломаться от unknown fields, проверяется в client SDK).

---

## OpenAPI и client generation

- FastAPI автоматически генерирует `/openapi.json`.
- Frontend Flutter получает его и через `openapi-generator-cli` генерирует Dart client (`pwa/lib/data/api/`).
- Регенерация — на каждый PR, как часть CI.
- Тесты Flutter используют `http_mock_adapter` для подмены реальных вызовов.

---

## Карта эндпоинтов (свод по спекам)

| Префикс | Спека | Главные ручки |
|---------|-------|---------------|
| `/api/v1/auth/**` | 001 | register, login, verify-email, forgot/reset-password, logout, account |
| `/api/v1/profile` | 002 | GET, PATCH, photo, complete-onboarding, export |
| `/api/v1/inbody/measurements/**` | 003, 013 | CRUD measurements, from-pdf upload+poll+confirm |
| `/api/v1/exercises/**` | 004 | list, by id, filters |
| `/api/v1/workouts/**` | 005 | start, finish, cancel, logs, replace, skip, history |
| `/api/v1/plans/**` | 006 | generate, active, by id, archive, history |
| `/api/v1/nutrition/**` | 007 | plans/generate, plans/active, meals/replace, dishes/alternatives |
| `/api/v1/forecast/inbody/**` | 008 | GET, what-if, history |
| `/api/v1/chat/**` | 009 | messages list/post, quick-replies |
| `/api/v1/adaptation/events` | 009 | list pending |
| `/api/v1/analytics/**` | 010 | inbody, workouts, exercise-progress, goal-progress, export-pdf |
| `/api/v1/notifications/**` | 011 | inbox, read, preferences, unsubscribe |
| `/api/v1/health` | (общий) | сервисный health |

Внутренние:
| Префикс | Назначение |
|---------|------------|
| `/internal/v1/workout-gen/**` | вызов ML модели Егора |
| `/internal/v1/inbody-pred/**` | вызов ML модели Маши |
| `/internal/v1/notifications/enqueue` | внутренний enqueue |
| `/internal/v1/adaptation/check-*` | вызов из beat |

---

## Обработка ошибок (примеры)

```python
# app/shared/errors.py
class AppError(Exception):
    status_code: int = 500
    error: str = "internal_error"

class ValidationError(AppError):
    status_code = 400
    error = "bad_request"

class NotFoundError(AppError):
    status_code = 404
    error = "not_found"

class ConflictError(AppError):
    status_code = 409
    error = "conflict"
```

Регистрируется глобальный exception handler, который мапит `AppError` в стандартный JSON-формат и логирует с `request_id`.

---

## Идемпотентность action-эндпоинтов

| Эндпоинт | Поведение при повторе |
|----------|------------------------|
| `POST /workouts/{id}/finish` (на already-finished) | 409 `workout_already_finished`, в `details.current_status` |
| `POST /plans/generate` (если активный план только что создан) | без `Idempotency-Key` создаёт новый и архивирует старый; с ключом — возвращает существующий |
| `POST /auth/forgot-password` (повторно) | всегда 200 с тем же сообщением (no-op user-visible) |
| `POST /chat/messages` | разрешает дубль (история сохраняет оба сообщения) |

---

## CORS

- Origin для PWA и API одинаковый (nginx обслуживает оба) — CORS не нужен.
- Если фронтенд переедет на отдельный домен — настроить `Access-Control-Allow-Origin: https://app.fitness.example.com`.
