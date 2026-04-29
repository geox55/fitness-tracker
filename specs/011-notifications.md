# Specification: Уведомления

**Epic:** E7 — Уведомления и интеграции
**User Story:** Пользователь должен получать своевременные напоминания (повторный InBody, обновление плана, мотивация) по email и in-app.
**Related specs:** [001-auth.md](001-auth.md), [003-inbody-measurements.md](003-inbody-measurements.md), [009-plan-adaptation-and-chat.md](009-plan-adaptation-and-chat.md)

---

## 1. User Goal

Пользователь не должен сам помнить, что пора пройти InBody снова или что план обновился. Приложение должно тактично напоминать и держать его в курсе. При этом — без спама.

---

## 2. Context

Канал доставки — email (через SendGrid) + in-app push (хранится как inbox внутри приложения). Web/PWA push notifications — out of scope в MVP.

Все типы уведомлений можно включать/выключать в настройках.

---

## 3. User Scenarios

### Scenario 1 — Напоминание о повторном InBody

**How to test independently**: В тестовой БД установить дату последнего InBody >30 дней назад, запустить cron-job, проверить что письмо отправлено и in-app inbox содержит сообщение.

**Acceptance criteria**:

1. **Given** прошло >30 дней с последнего InBody-измерения у пользователя.
   **When** срабатывает scheduled job (раз в сутки).
   **Then** отправляется email «Пора повторить InBody-анализ» и создаётся in-app сообщение.

2. **Given** уведомление этого типа уже отправлено за последние 7 дней этому пользователю.
   **When** проходит scheduled job.
   **Then** повторно не отправляется (debounce).

3. **Given** пользователь отключил уведомления о повторном InBody.
   **When** триггер срабатывает.
   **Then** уведомление не отправляется.

### Scenario 2 — Уведомление об автоматической регенерации плана

**Acceptance criteria**:

1. **Given** план был автоматически перегенерирован (см. [009](009-plan-adaptation-and-chat.md)).
   **When** регенерация завершена.
   **Then** отправляется email + in-app «Ваш план обновлён» с краткой сводкой изменений и CTA «Открыть план».

### Scenario 3 — Уведомление о подтверждении email

См. [001-auth.md](001-auth.md).

### Scenario 4 — Сброс пароля

См. [001-auth.md](001-auth.md).

### Scenario 5 — Еженедельное саммари

**Acceptance criteria**:

1. **Given** прошёл понедельник 09:00 по таймзоне пользователя (или UTC если таймзона неизвестна).
   **When** срабатывает scheduled job.
   **Then** отправляется in-app сообщение (опц. email, по настройке) с саммари прошлой недели: число тренировок, тоннаж, дельта веса, новые достижения.

2. **Given** на прошлой неделе тренировок не было.
   **When** срабатывает job.
   **Then** отправляется поддерживающее сообщение, не саммари.

### Scenario 6 — Управление уведомлениями

**Acceptance criteria**:

1. **Given** пользователь в настройках.
   **When** он переключает тоглы по типам уведомлений (`inbody_reminder`, `plan_update`, `weekly_summary`).
   **Then** настройка сохраняется; следующие триггеры этого типа уважают настройку.

2. **Given** пользователь нажал «Отписаться от всех» в email.
   **When** он переходит по ссылке.
   **Then** все email-уведомления отключаются (in-app остаются).

### Scenario 7 — Inbox в приложении

**Acceptance criteria**:

1. **Given** есть непрочитанные in-app сообщения.
   **When** пользователь открывает иконку колокольчика.
   **Then** видит список с непрочитанными сверху; тап на сообщение помечает прочитанным и уводит на соответствующий экран (план/InBody/...).

---

## 4. Functional Requirements

| #      | Requirement                                                                                                  |
|--------|--------------------------------------------------------------------------------------------------------------|
| REQ-01 | Канал email через SendGrid (или альтернативный SMTP-провайдер)                                                 |
| REQ-02 | In-app inbox с непрочитанными/прочитанными                                                                    |
| REQ-03 | Тип `email_verify`: см. [001](001-auth.md)                                                                    |
| REQ-04 | Тип `password_reset`: см. [001](001-auth.md)                                                                  |
| REQ-05 | Тип `inbody_reminder`: триггер «прошло >30 дней с последнего InBody», debounce 7 дней                         |
| REQ-06 | Тип `plan_update`: триггер «план был автоматически перегенерирован»                                            |
| REQ-07 | Тип `weekly_summary`: scheduled понедельник 09:00 (по timezone пользователя или UTC fallback)                 |
| REQ-08 | Настройки пользователя: вкл/выкл по каждому типу (кроме transactional типов из auth — они всегда on)         |
| REQ-09 | Универсальная ссылка «Отписаться» в email                                                                      |
| REQ-10 | Шаблоны email на русском (MVP); поддержка других языков в фазе 2                                                |
| REQ-11 | Аудит-лог отправок (тип, кому, когда, статус доставки от SendGrid)                                              |
| REQ-12 | Запрет дублирования: тот же тип + тот же контекст-key не отправляется повторно в дебаунс-окне                  |

---

## 5. Non-functional Requirements

| #      | Requirement                                                                  | Category    |
|--------|------------------------------------------------------------------------------|-------------|
| NFR-01 | Очередь отправки на стороне сервиса; ретраи при ошибках SendGrid              | Reliability |
| NFR-02 | Отправка не блокирует основной API (асинхронно, через очередь/worker)         | Performance |
| NFR-03 | PII в email шифруется на провайдере, при возможности — minimum data           | Privacy     |
| NFR-04 | Time-to-deliver email ≤2 минут на 95-перцентиле                               | Performance |

---

## 6. Data Model

**Entity: NotificationPreferences**

| Field            | Type     | Constraints              | Description                                  |
|------------------|----------|--------------------------|----------------------------------------------|
| user_id          | UUID     | PK + FK → User           |                                              |
| inbody_reminder  | Boolean  | Default true             |                                              |
| plan_update      | Boolean  | Default true             |                                              |
| weekly_summary   | Boolean  | Default true             |                                              |
| email_enabled    | Boolean  | Default true             | Глобальный тоглл всех email                  |

**Entity: NotificationOutbox**

| Field          | Type      | Constraints                                                  | Description                                     |
|----------------|-----------|--------------------------------------------------------------|-------------------------------------------------|
| id             | UUID      | PK                                                           |                                                 |
| user_id        | UUID      | FK → User                                                    |                                                 |
| type           | Enum      | `email_verify` \| `password_reset` \| `inbody_reminder` \| `plan_update` \| `weekly_summary` |          |
| channel        | Enum      | `email` \| `in_app`                                          |                                                 |
| context_key    | String    | Required                                                     | Уникализация (например `inbody_reminder:2026-04-28`) — для debounce |
| payload        | JSON      | Required                                                     | Данные для рендеринга шаблона                   |
| status         | Enum      | `queued` \| `sent` \| `failed` \| `bounced`                  |                                                 |
| sent_at        | Timestamp | Optional                                                     |                                                 |
| read_at        | Timestamp | Optional                                                     | Только для in_app                               |
| created_at     | Timestamp | Required                                                     |                                                 |

---

## 7. Screens

### Screen: Inbox

**Elements**:
- Список сообщений с иконкой типа, заголовком, кратким текстом, временем
- Бейдж непрочитанных
- Тап → переход на соответствующий экран продукта
- Свайп → удалить

### Screen: Настройки уведомлений

**Elements**: тоглы по каждому типу + глобальный тогл email.

---

## 9. API Endpoints

### Inbox

```
GET /api/v1/notifications/inbox?unread=true&limit=20
```

```
POST /api/v1/notifications/{id}/read
```

```
DELETE /api/v1/notifications/{id}
```

### Настройки

```
GET /api/v1/notifications/preferences
PATCH /api/v1/notifications/preferences
{ "inbody_reminder": false }
```

### Отписаться по email-ссылке

```
GET /api/v1/notifications/unsubscribe?token=...
```
Открывает простую веб-страницу с подтверждением, токен одноразовый.

### Внутренний (для cron / watchers)

```
POST /internal/v1/notifications/enqueue
{ "user_id": "...", "type": "inbody_reminder", "context_key": "...", "payload": {...} }
```

---

## 10. Edge Cases

- Пользователь удалил аккаунт → outbox-записи удаляются вместе с ним; уже отправленные письма не отзываются (физически нельзя).
- SendGrid bounce (несуществующий email) → статус `bounced`, повторно не пробуем; в админ-логе.
- Пользователь не подтвердил email → отправляются только transactional (`email_verify`, `password_reset`); `inbody_reminder` и т.д. — не до подтверждения.
- Включена только in-app, email выключен → inbody_reminder показывается только в inbox.
- Пользователь нажимает «Отписаться» из письма → отключается только email-канал; in-app продолжает работать.

---

## 11. Out of Scope

- Web push / PWA push notifications (фаза 2)
- iOS/Android native push (мобильные приложения вне MVP, продукт — PWA)
- SMS-уведомления
- Уведомления о пропущенных тренировках («ты не был в зале 5 дней») — фаза 2
- Уведомления тренеру / третьему лицу
- A/B-тесты на текстах писем
- Подробная аналитика open/click rate — стандартный SendGrid dashboard, не наша поверхность
