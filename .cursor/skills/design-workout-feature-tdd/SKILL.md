---
name: design-workout-feature-tdd
description: Generates test cases, API structure, and draft DB schema for new workout-related features from a markdown feature description. Use when the user describes a new fitness/workout feature and needs a TDD-friendly design broken into Tests, API, and DB blocks.
---

# Design Workout Feature (TDD)

## When to Use

Use this skill when:
- The user provides a **markdown description of a new feature** for the Fitness Tracker (e.g. "логирование подходов с RPE", "отчёт по прогрессу за месяц").
- The feature **затрагивает домен тренировок**: упражнения, подходы, сеты, RPE, планы тренировок, прогресс, статистику и т.п.
- Нужно быстро набросать **TDD‑дизайн**: список тест‑кейсов, API‑контракты и черновик схем БД.

Do **not** use this skill:
- Для общих UI‑правок без изменения доменной логики.
- Для мелких копий уже существующих эндпоинтов, где проще скопировать и адаптировать текущую схему.

## Input Expectations

The input is a **markdown feature spec** with:
- **Goal / user story**: кто и зачем использует фичу.
- **Main flows**: базовый сценарий + важные ветки (ошибки, ограничения).
- **Domain terms**: названия сущностей (set, exercise, workout, RPE, volume, PR, и т.п.).

If details are missing:
- Make **reasonable, explicit assumptions** in the output (prefix with “Assumption:”).
- Prefer **consistency** with existing patterns in the Fitness Tracker project (controller → service → repository, shared schemas/types, unified API error format).

## Output Format (Always Use)

Always answer in **one message** with **three top-level sections** in this strict order:

1. `## Tests`
2. `## API`
3. `## DB`

Do **not** add other top-level sections. Inside each section, follow the templates below.

### 1. `## Tests` Section

Purpose: задать TDD‑рамку. Сначала думаем тестами, потом API и БД.

Structure:
- Start with a short **overview paragraph**: what we are validating for this feature.
- Then provide two subsections:
  - `### Happy Path`
  - `### Edge Cases & Errors`

For each subsection:
- Use a **numbered list** of test cases.
- Each item should follow this template:

```markdown
1. **[Scope] краткое название теста**
   - Given: начальное состояние / входные данные
   - When: действие пользователя / вызов API
   - Then: ожидаемый результат (ответ API, изменения в БД, инварианты)
```

Guidelines:
- **Scope examples**: `[API]`, `[Service]`, `[Repository]`, `[E2E]`.
- Покрой:
  - базовый happy path (успешный лог, фетч списка, обновление и т.п.);
  - валидационные ошибки (некорректные поля, лимиты, обязательные значения);
  - авторизацию/аутентификацию, если фича зависит от сессии;
  - важные инварианты домена (например, RPE 1–10, вес > 0, нельзя логировать в прошлое/будущее за пределами заданного диапазона).

### 2. `## API` Section

Purpose: описать HTTP‑контракт, который будет реализован в backend (Fastify, Controller → Service → Repository).

Structure:
- Start with a short **overview paragraph**: what endpoints are needed and how they map to the tests.
- Then list endpoints grouped by method:
  - `### POST`
  - `### GET`
  - `### PATCH`
  - `### DELETE`
  - (include only the methods actually needed.)

For each endpoint, use this template:

```markdown
- **[METHOD] /api/...**
  - Purpose: кратко, что делает эндпоинт
  - Auth: `required` | `optional` | `none`
  - Request:
    - Query: `{ ... }` (если нужно, иначе `-`)
    - Body (TS type / Zod‑схема черновик):
      ```ts
      type RequestBody = {
        // поля и их ограничения, опциональные vs обязательные
      }
      ```
  - Responses:
    - 200:
      ```ts
      type SuccessResponse = {
        data: { ... }
        total?: number
        hasMore?: boolean
      }
      ```
    - 4xx/5xx (основные):
      ```ts
      type ErrorResponse = {
        error: string
        code?: string  // например "validation_error" | "not_found" | ...
        details?: object
      }
      ```
  - Validation notes:
    - Ключевые правила валидации (диапазоны, зависимости полей, уникальность, и т.п.)
  - Error cases:
    - Список доменных ошибок, которые важны для клиента (например, `EXERCISE_NOT_FOUND`, `INVALID_RPE_RANGE`).
```

Guidelines:
- Используй **существующие паттерны проекта**: единый формат `{ data }` / `{ error }`, UUID‑ы, ISO‑даты, Zod‑валидацию.
- Явно привязывай эндпоинты к тест‑кейсам из секции `## Tests` (можно ссылаться по названию теста).

### 3. `## DB` Section

Purpose: накидать первичный дизайн сущностей/таблиц под фичу.

Structure:
- Start with a short **overview paragraph**: какие новые сущности / связи добавляем или какие существующие затрагиваем.
- Then define tables using this template:

```markdown
### Table: table_name

- Purpose: краткое описание роли таблицы
- Columns:
  - `id` (PK, string, UUID)
  - `column_name` (тип, ограничения, nullable/нет)
  - ...
- Indexes:
  - `idx_table_column` (описание, зачем нужен)
- Relations:
  - FK: `table.column` → `other_table.id` (onDelete / onUpdate стратегии)
```

Guidelines:
- Используй именование, совместимое с текущим проектом (snake_case в БД, UUID для идентификаторов).
- Учитывай:
  - Историчность данных (нужно ли хранить историю изменений или достаточно текущего состояния).
  - Потенциальные агрегации для аналитики (индексы по дате, упражнению, пользователю).
  - Связи с уже существующими сущностями (`workouts`, `exercises`, `workout_sessions`, и т.п. — если они упоминаются во входном описании).
- Если не уверен, явно укажи **Assumption** возле спорных полей или связей.

## Example Usage (Conceptual)

Given a feature description like:

> Пользователь хочет логировать каждый подход с весом, повторениями и RPE,  
> чтобы потом видеть прогресс по конкретному упражнению.

The output should be structured as:

```markdown
## Tests
...список тест‑кейсов (happy path + edge cases)...

## API
...список эндпоинтов с payload, ответами и ошибками...

## DB
...черновые таблицы/set‑сущности, связи и индексы...
```

Make sure:
- All three sections are present.
- The structure within each section matches the templates above.
- Assumptions are clearly labeled and biased toward consistency with the existing Fitness Tracker architecture and API patterns.

