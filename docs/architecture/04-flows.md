# Key Flows — Sequence Diagrams

Диаграммы взаимодействий для ключевых сценариев. Все диаграммы используют:
- `client` — Flutter PWA
- `api` — FastAPI монолит
- `worker` — Celery worker
- `ml` — ml-inference сервис
- `pg` — PostgreSQL
- `redis` — Redis
- `minio` — MinIO
- `sg` — SendGrid

---

## 1. Регистрация и подтверждение email (spec 001)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg
    participant Redis as redis
    participant Worker as worker
    participant Sg as SendGrid

    Client->>Api: POST /auth/register {email, password}
    Api->>Pg: INSERT users (email_status=unconfirmed)
    Api->>Pg: INSERT auth_tokens (type=email_verify)
    Api->>Redis: enqueue send_email(verify, token)
    Api-->>Client: 201 {user_id, email_status:unconfirmed}

    Worker->>Redis: dequeue send_email
    Worker->>Pg: read auth_token + payload
    Worker->>Sg: POST send {to, template, vars}
    Sg-->>Worker: 200 OK
    Worker->>Pg: UPDATE notification_outbox status=sent

    Note over Client: Пользователь открывает ссылку из письма
    Client->>Api: POST /auth/verify-email {token}
    Api->>Pg: SELECT auth_token by token_hash
    Api->>Pg: UPDATE users SET email_status=active
    Api->>Pg: UPDATE auth_tokens SET used_at=now()
    Api->>Pg: INSERT auth_tokens (type=session) + (type=refresh)
    Api-->>Client: 200 {access_token, refresh_token}
```

---

## 2. Логин с rate limiting (spec 001)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Redis as redis
    participant Pg as pg

    Client->>Api: POST /auth/login {email, password}
    Api->>Redis: INCR login_attempts:{ip}:{email}, TTL 600
    alt > 5 попыток
        Api-->>Client: 429 rate_limited (retry_after=900)
    else
        Api->>Pg: SELECT user by email
        alt user not found OR password mismatch
            Api-->>Client: 401 invalid_credentials
        else email not confirmed
            Api-->>Client: 403 email_unconfirmed
        else OK
            Api->>Pg: INSERT auth_tokens (session, refresh)
            Api->>Redis: DEL login_attempts:{ip}:{email}
            Api-->>Client: 200 {access_token, refresh_token}
        end
    end
```

---

## 3. Загрузка PDF InBody (spec 003, 013)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg
    participant Minio as minio
    participant Redis as redis
    participant Worker as worker

    Client->>Api: POST /inbody/measurements/from-pdf<br/>(multipart, file)
    Api->>Minio: PUT inbody-pdf-temp/{user_id}/{job_id}.pdf
    Api->>Pg: INSERT pdf_import_jobs (status=parsing, temp_pdf_url)
    Api->>Redis: enqueue parse_inbody_pdf(job_id)
    Api-->>Client: 202 {job_id, status: parsing}

    Worker->>Redis: dequeue parse_inbody_pdf
    Worker->>Pg: SELECT pdf_import_jobs WHERE id=job_id
    Worker->>Minio: GET inbody-pdf-temp/{key}
    Worker->>Worker: pdfplumber → match templates
    Worker->>Pg: UPDATE status=ready/partial/failed,<br/>extracted, missing_fields, template

    loop client polls
        Client->>Api: GET /inbody/measurements/from-pdf/{job_id}
        Api->>Pg: SELECT pdf_import_jobs
        Api-->>Client: 200 {status, extracted, missing_fields}
    end

    Note over Client: Пользователь правит и подтверждает
    Client->>Api: POST /inbody/measurements/from-pdf/{job_id}/confirm<br/>{final values}
    Api->>Pg: BEGIN
    Api->>Minio: COPY inbody-pdf-temp/* → inbody-pdf/*
    Api->>Pg: INSERT inbody_measurements (source=pdf, original_pdf_url)
    Api->>Pg: UPDATE pdf_import_jobs SET confirmed_at, confirmed_measurement_id
    Api->>Pg: COMMIT
    Api->>Minio: DELETE inbody-pdf-temp/* (best-effort)
    Api-->>Client: 201 {measurement_id, ...}

    Note over Api: Триггер adaptation (см. flow 6)
```

---

## 4. Генерация плана тренировок (spec 006)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg
    participant Ml as ml
    participant Redis as redis

    Client->>Api: POST /plans/generate
    Api->>Pg: SELECT user_profiles + last inbody_measurement
    alt no profile or no inbody
        Api-->>Client: 400 preconditions_not_met
    end
    Api->>Pg: SELECT exercises WHERE equipment ⊆ available
    Api->>Redis: GET cache:plan:{user_id}:{features_hash}
    alt cache hit
        Api-->>Client: 201 {plan from cache}
    else
        Api->>Ml: POST /workout-gen/generate {features, history, exercise_pool, seed}
        alt timeout > 12s
            Ml--xApi: timeout
            Api->>Api: rule_based_fallback()
            Note over Api: fallback=true
        else OK
            Ml-->>Api: 200 {weeks: [...]}
        end
        Api->>Api: validate plan (lint)
        alt validation fails (≤3 retries)
            Api->>Ml: retry с другим seed
        end
        Api->>Pg: BEGIN
        Api->>Pg: UPDATE workout_plans SET status=archived WHERE active
        Api->>Pg: INSERT workout_plans (active, model_version, input_features)
        Api->>Pg: INSERT plan_weeks → plan_days → plan_exercises (×4×N×M)
        Api->>Pg: COMMIT
        Api->>Redis: SET cache:plan TTL 24h
        Api-->>Client: 201 {plan_id, weeks: [...]}
    end
```

---

## 5. Прогноз InBody (spec 008)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg
    participant Redis as redis
    participant Ml as ml

    Client->>Api: GET /forecast/inbody?horizons=1,2,4
    Api->>Pg: SELECT inbody_measurements (последние 12 недель)
    alt 0 measurements
        Api-->>Client: 404 not_enough_data
    end
    Api->>Redis: GET cache:forecast:{user_id}:{last_inbody_id}
    alt cache hit
        Api-->>Client: 200 {forecast}
    else
        Api->>Pg: SELECT workouts + exercise_logs (агрегаты по неделям)
        Api->>Pg: SELECT user_profiles
        Api->>Ml: POST /inbody-pred/forecast {features, history, horizons}
        alt timeout > 5s
            Ml--xApi: timeout
            Api->>Api: linear_baseline()
            Note over Api: fallback=true, confidence=low
        else OK
            Ml-->>Api: 200 {metrics: {...}, confidence}
        end
        Api->>Pg: INSERT inbody_forecasts (×3 metrics × 3 horizons = 9 rows)
        Api->>Redis: SET cache:forecast TTL 24h
        Api-->>Client: 200 {forecast, confidence, fallback}
    end
```

---

## 6. Адаптация плана при новом InBody (spec 009)

```mermaid
sequenceDiagram
    participant Api as api
    participant Pg as pg
    participant Redis as redis
    participant Worker as worker
    participant Ml as ml

    Note over Api: внутри транзакции confirm нового InBody
    Api->>Pg: SELECT prev_inbody, new_inbody
    Api->>Api: delta = |new.weight - prev.weight|

    alt delta > 2kg OR > 3% за <30d
        Api->>Pg: INSERT plan_rebuild_events<br/>(trigger=weight_change, target=nutrition, status=pending)
        Api->>Redis: enqueue process_plan_rebuild_event(event_id)
        Api->>Pg: SET user_profiles.plan_rebuild_required=true (для workout)
    else
        Api->>Redis: enqueue recompute_forecast(user_id)
    end

    Note over Worker: асинхронная обработка
    Worker->>Redis: dequeue process_plan_rebuild_event
    Worker->>Pg: SELECT event + user features
    Worker->>Worker: regenerate_nutrition_plan() (rule-based)
    Worker->>Pg: BEGIN
    Worker->>Pg: UPDATE nutrition_plans status=archived WHERE active
    Worker->>Pg: INSERT new nutrition_plan + nutrition_days + meals
    Worker->>Pg: UPDATE plan_rebuild_events status=auto_applied, applied_at
    Worker->>Pg: INSERT notification_outbox (type=plan_update)
    Worker->>Pg: COMMIT
    Worker->>Redis: enqueue send_email
```

---

## 7. Cron-триггеры (Celery Beat) (spec 011)

```mermaid
sequenceDiagram
    participant Beat as beat
    participant Redis as redis
    participant Worker as worker
    participant Pg as pg
    participant Sg as SendGrid

    Note over Beat: Каждый день 06:00 UTC
    Beat->>Redis: enqueue check_inbody_reminders

    Worker->>Redis: dequeue
    Worker->>Pg: SELECT users<br/>WHERE last_inbody.measured_at < now()-30d<br/>AND notification_preferences.inbody_reminder=true<br/>AND NOT EXISTS recent reminder (debounce 7d)
    loop для каждого user
        Worker->>Pg: INSERT notification_outbox (inbody_reminder, in_app)
        Worker->>Pg: INSERT notification_outbox (inbody_reminder, email)
        Worker->>Sg: POST send (email)
        Worker->>Pg: UPDATE outbox status=sent
    end
```

---

## 8. Старт и завершение тренировки (spec 005)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg

    Note over Client,Api: Старт
    Client->>Api: POST /workouts {origin: plan, plan_day_id}
    Api->>Pg: SELECT plan_day → exercises
    Api->>Pg: INSERT workouts (status=in_progress)
    Api-->>Client: 201 {workout, planned_exercises}

    loop для каждого подхода
        Client->>Api: POST /workouts/{id}/logs {exercise_id, set, reps, weight, rpe}
        Api->>Pg: INSERT exercise_logs
        Api-->>Client: 201
    end

    Note over Client,Api: Завершение
    Client->>Api: POST /workouts/{id}/finish
    Api->>Pg: UPDATE workouts SET status=completed, finished_at=now()
    Api->>Pg: SELECT aggregate (длительность, тоннаж, число подходов)
    Api-->>Client: 200 {workout, summary}
```

### Авто-завершение (через 12ч простоя)

```mermaid
sequenceDiagram
    participant Beat as beat
    participant Worker as worker
    participant Pg as pg

    Note over Beat: Каждый час
    Beat->>Worker: enqueue auto_finish_stale_workouts
    Worker->>Pg: SELECT workouts WHERE status=in_progress<br/>AND no recent log > 12h
    loop каждая
        Worker->>Pg: UPDATE workouts SET status=auto_finished, finished_at=last_log+12h
        Worker->>Pg: INSERT notification_outbox (in_app)
    end
```

---

## 9. Чат-ассистент: scripted vs LLM (spec 009)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg
    participant Llm as LLM provider

    Client->>Api: POST /chat/messages {content}
    Api->>Pg: INSERT chat_messages (author=user)
    Api->>Api: scripted_matcher(content)
    alt match found
        Api->>Pg: SELECT user context (profile, plan)
        Api->>Api: render_template(template_id, context)
        Api->>Pg: INSERT chat_messages (author=assistant, source=scripted)
        Api-->>Client: 200 [user_msg, assistant_msg]
    else no match AND LLM enabled
        Api->>Api: build_prompt(anonymized context)
        Api->>Llm: completions
        alt timeout > 15s OR error
            Api->>Pg: INSERT chat_messages (source=scripted, "Я пока не умею...")
            Api-->>Client: 200 [..., default_msg]
        else OK
            Llm-->>Api: text
            Api->>Api: append disclaimer
            Api->>Pg: INSERT chat_messages (source=llm)
            Api-->>Client: 200 [user_msg, assistant_msg]
        end
    else LLM disabled
        Api->>Pg: INSERT chat_messages (source=scripted, default)
        Api-->>Client: 200
    end
```

---

## 10. Экспорт PDF-отчёта (spec 010)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg
    participant Redis as redis
    participant Worker as worker
    participant Minio as minio

    Client->>Api: POST /analytics/export-pdf {from, to, sections}
    Api->>Pg: INSERT export_pdf_jobs (status=queued)
    Api->>Redis: enqueue generate_analytics_pdf(job_id)
    Api-->>Client: 202 {job_id}

    Worker->>Redis: dequeue
    Worker->>Pg: SELECT все агрегаты + InBody + workouts
    Worker->>Worker: render HTML template (Jinja2)
    Worker->>Worker: weasyprint HTML→PDF
    Worker->>Minio: PUT analytics-reports/{user_id}/{job_id}.pdf
    Worker->>Pg: UPDATE export_pdf_jobs SET status=ready, s3_key

    loop client polls
        Client->>Api: GET /analytics/export-pdf/{job_id}
        Api->>Pg: SELECT job
        alt status=ready
            Api->>Minio: presigned_url(s3_key, ttl=1h)
            Api-->>Client: 200 {status:ready, url, expires_at}
        else
            Api-->>Client: 200 {status:processing}
        end
    end
```

---

## 11. GDPR-удаление аккаунта (spec 002)

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api
    participant Pg as pg
    participant Beat as beat
    participant Worker as worker
    participant Minio as minio

    Client->>Api: DELETE /auth/account {password}
    Api->>Pg: verify password
    Api->>Pg: UPDATE users SET deleted_at=now()
    Api->>Pg: DELETE auth_tokens WHERE user_id=...
    Api-->>Client: 204

    Note over Beat: ежедневный cron, ≥30 дней спустя
    Beat->>Worker: enqueue gdpr_purge_users
    Worker->>Pg: SELECT users WHERE deleted_at < now() - 30d
    loop каждый
        Worker->>Pg: BEGIN
        Worker->>Pg: DELETE FROM users WHERE id=...<br/>(CASCADE удаляет всё связанное)
        Worker->>Pg: COMMIT
        Worker->>Minio: DELETE префиксы user_id/* во всех buckets
    end
```

---

## 12. Высокоуровневая страница «Сегодня» (spec 005, 006, 007)

Это не отдельный flow, а композиция нескольких read-only запросов, которые клиент делает в параллель при открытии главного экрана:

```mermaid
sequenceDiagram
    participant Client as client
    participant Api as api

    par
        Client->>Api: GET /profile
    and
        Client->>Api: GET /plans/active
    and
        Client->>Api: GET /nutrition/plans/active
    and
        Client->>Api: GET /forecast/inbody?horizons=4
    and
        Client->>Api: GET /notifications/inbox?unread=true
    end

    Note over Client: Параллельные запросы, результаты собираются в Riverpod-провайдеры,<br/>UI отображается прогрессивно по мере прихода
```
