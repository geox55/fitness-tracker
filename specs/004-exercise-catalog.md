# Specification: Каталог упражнений

**Epic:** E2 — Тренировки
**User Story:** Пользователь должен иметь доступ к справочнику упражнений с описанием, техникой и группой мышц, чтобы понимать, что и как делать в тренировке (и чтобы AI-генератор имел из чего выбирать).
**Related specs:** [005-workout-tracking.md](005-workout-tracking.md), [006-ai-workout-generator.md](006-ai-workout-generator.md), [012-ml-dataset.md](012-ml-dataset.md)

---

## 1. User Goal

Пользователь видит в плане тренировок незнакомое упражнение и хочет посмотреть, как оно делается. Он открывает карточку, видит описание, технику, целевые мышцы и оборудование. Также пользователь может искать упражнения вручную (например, чтобы добавить в тренировку «свободный» подход) и фильтровать по группе мышц/оборудованию.

Каталог одновременно — это knowledge base для AI-генератора: модель выбирает упражнения из этого пула.

---

## 2. Context

Каталог наполняется из объединённого датасета (см. [012-ml-dataset.md](012-ml-dataset.md)) — Kaggle-датасеты + API Ninjas, нормализованные в одну схему. Это reference data: пользователь не может создавать собственные упражнения в MVP (только команда — через сидинг БД).

---

## 3. User Scenarios

### Scenario 1 — Просмотр упражнения из плана

В плане тренировок пользователь видит «Жим штанги лёжа» и хочет почитать про него.

**How to test independently**: Открыть любую тренировку, тапнуть по упражнению, проверить открытие карточки со всеми полями.

**Acceptance criteria**:

1. **Given** пользователь в карточке тренировки.
   **When** он тапает на упражнение.
   **Then** открывается карточка упражнения с полями: название, основная группа мышц, дополнительные мышцы, описание, техника, оборудование, регион тела, kcal/час.

2. **Given** упражнение есть в каталоге.
   **When** карточка открывается.
   **Then** все обязательные поля заполнены; необязательные могут быть пустыми (отсутствие отображается как «—»).

### Scenario 2 — Поиск упражнения по названию

Пользователь хочет добавить «приседания» в свою тренировку.

**How to test independently**: Открыть каталог, ввести в поиск «присед», проверить релевантные результаты.

**Acceptance criteria**:

1. **Given** пользователь на экране каталога.
   **When** он вводит в поиск «присед» (≥2 символа).
   **Then** список фильтруется по подстроке в `exercise_name` (case-insensitive, поддержка кириллицы и латиницы).

2. **Given** запрос ничего не находит.
   **When** список пуст.
   **Then** показывается empty state «Ничего не нашлось. Попробуйте другое название».

### Scenario 3 — Фильтр по группе мышц / оборудованию

Пользователь работает дома без штанги — хочет видеть только упражнения с гантелями и собственным весом.

**How to test independently**: Открыть каталог, активировать фильтры, проверить корректную фильтрацию.

**Acceptance criteria**:

1. **Given** пользователь на экране каталога.
   **When** он выбирает фильтры: группа мышц = «грудь», оборудование = «гантели».
   **Then** список сужается до упражнений, у которых `primary_muscle_group = chest` и `equipment` содержит `dumbbell`.

2. **Given** включено несколько значений в одном фильтре.
   **When** применяется фильтр.
   **Then** работает как OR внутри фильтра, AND между разными фильтрами.

3. **Given** фильтр сброшен.
   **When** пользователь жмёт «Очистить».
   **Then** показывается полный каталог.

### Scenario 4 — Подбор упражнений по доступному оборудованию (для AI)

Этот сценарий — машинный, но описан здесь, потому что использует ту же модель данных.

**How to test independently**: Создать тестового пользователя с тегом «домашний зал» (только гантели + турник), сгенерировать план, проверить что в нём нет упражнений со штангой.

**Acceptance criteria**:

1. **Given** AI-генератор формирует план для пользователя с настройкой `equipment_available = [dumbbell, bodyweight, pullup_bar]`.
   **When** модель выбирает упражнения.
   **Then** в плане только те, у которых `equipment ⊆ equipment_available`.

(Сама генерация описана в [006-ai-workout-generator.md](006-ai-workout-generator.md).)

---

## 4. Functional Requirements

| #      | Requirement                                                                                    |
|--------|------------------------------------------------------------------------------------------------|
| REQ-01 | Каталог содержит ≥500 упражнений после объединения датасетов (см. [012](012-ml-dataset.md))    |
| REQ-02 | Каждое упражнение имеет поля: id, name, primary_muscle_group, secondary_muscle_group, instructions, equipment, calories_burned_per_hour, body_region |
| REQ-03 | Поиск по названию (substring, case-insensitive, поддержка ru + en)                              |
| REQ-04 | Фильтр по primary_muscle_group (multi-select)                                                  |
| REQ-05 | Фильтр по equipment (multi-select)                                                             |
| REQ-06 | Фильтр по body_region (multi-select)                                                            |
| REQ-07 | Список с пагинацией: 30 элементов на страницу                                                   |
| REQ-08 | Карточка упражнения с полным описанием и техникой выполнения                                    |
| REQ-09 | Поле `equipment_available` в профиле пользователя для фильтрации в AI-генерации                 |

---

## 5. Non-functional Requirements

| #      | Requirement                                                                              | Category    |
|--------|------------------------------------------------------------------------------------------|-------------|
| NFR-01 | Поиск по 500 упражнениям ≤200 ms на 95-перцентиле                                         | Performance |
| NFR-02 | Каталог работает офлайн (закешированные данные на клиенте, обновление при онлайне)        | UX          |
| NFR-03 | Все строки `instructions` доступны как минимум на английском (русский — по возможности)   | I18n        |

---

## 6. Data Model

**Entity: Exercise**

| Field                    | Type     | Constraints                                                  | Description                                                  |
|--------------------------|----------|--------------------------------------------------------------|--------------------------------------------------------------|
| id                       | UUID     | PK                                                           | Внутренний ID                                                |
| exercise_id              | String   | Unique, required                                             | Стабильный slug (для импорта/обновления из датасета)         |
| exercise_name            | String   | Required, 2..120 chars                                       |                                                              |
| exercise_name_ru         | String   | Optional                                                     | Локализация на русский (если есть)                           |
| primary_muscle_group     | Enum     | Required, см. enum ниже                                      | Главная группа мышц                                          |
| secondary_muscle_group   | Enum[]   | Optional                                                     | Дополнительные группы                                        |
| instructions             | Text     | Required                                                     | Пошаговая техника                                            |
| equipment                | Enum[]   | Required, ≥1                                                  | Какое оборудование нужно                                     |
| calories_burned_per_hour | Number   | Optional, 50..2000                                           | Оценочное значение для пользователей средней массы           |
| body_region              | Enum     | Required, `upper` \| `lower` \| `core` \| `full_body`        |                                                              |
| difficulty               | Enum     | Optional, `beginner` \| `intermediate` \| `advanced`         | Если есть в источнике                                        |
| source_dataset           | String   | Required                                                     | `kaggle_ambarish` \| `kaggle_omarxadel` \| `api_ninjas` \| `merged` |

**Enum: muscle_group**
`chest`, `back`, `shoulders`, `biceps`, `triceps`, `forearms`, `quads`, `hamstrings`, `glutes`, `calves`, `abs`, `obliques`, `lats`, `traps`, `lower_back`, `cardio`.

**Enum: equipment**
`barbell`, `dumbbell`, `kettlebell`, `machine`, `cable`, `bodyweight`, `bench`, `pullup_bar`, `dip_bars`, `resistance_band`, `medicine_ball`, `treadmill`, `stationary_bike`, `rowing_machine`, `other`.

---

## 7. Screens

### Screen: Каталог упражнений

**Purpose**: Поиск и фильтрация упражнений.

**Elements**:
- Поисковая строка сверху
- Кнопка «Фильтры» → bottom sheet с группой мышц / оборудованием / регионом тела
- Список карточек: иконка/превью, название, primary muscle, equipment chips
- Пагинация (infinite scroll)

**States**:
- Loading: skeleton-карточки
- Empty (по фильтрам): «Ничего не нашлось»
- Error: «Не удалось загрузить» + retry

### Screen: Карточка упражнения

**Elements**:
- Заголовок (название) + название EN курсивом
- Чипы: primary/secondary muscles, equipment, body region, difficulty
- Секция «Техника выполнения» (markdown-текст)
- Опционально: kcal/час
- Кнопка «Добавить в тренировку» (если открыто из workflow тренировки) — см. [005](005-workout-tracking.md)

---

## 9. API Endpoints

### Поиск/список

```
GET /api/v1/exercises?q=присед&muscle_group=quads&equipment=barbell,bodyweight&body_region=lower&limit=30&offset=0
```

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "exercise_id": "barbell_squat",
      "exercise_name": "Barbell Back Squat",
      "exercise_name_ru": "Приседания со штангой",
      "primary_muscle_group": "quads",
      "secondary_muscle_group": ["glutes", "hamstrings"],
      "equipment": ["barbell", "bench"],
      "body_region": "lower",
      "calories_burned_per_hour": 380
    }
  ],
  "total": 142
}
```

### Получить одно

```
GET /api/v1/exercises/{id}
```

**Response 200**: полный объект Exercise с `instructions`.

### Метаданные фильтров

```
GET /api/v1/exercises/filters
```

**Response 200**:
```json
{
  "muscle_groups": ["chest", "back", ...],
  "equipment": ["barbell", "dumbbell", ...],
  "body_regions": ["upper", "lower", "core", "full_body"]
}
```

---

## 10. Edge Cases

- В исходных датасетах одно и то же упражнение под разными названиями («Bench press», «Barbell bench press flat») → дедупликация при сидинге, см. [012](012-ml-dataset.md).
- В части записей `calories_burned_per_hour` отсутствует → показывать «—», не блокировать.
- Пользователь работает офлайн → отдаём кешированный snapshot каталога.
- Поисковый запрос на русском, но имена упражнений только на английском → требовать `exercise_name_ru` для топ-200 упражнений (см. [012](012-ml-dataset.md)).

---

## 11. Out of Scope

- Видео-демонстрация упражнений (см. open question #2 в overview)
- Пользовательские упражнения (user-created)
- Рейтинги, отзывы, сложность от сообщества
- 3D-анатомия / интерактивная модель
- Альтернативы упражнения («заменить на похожее») — отдельная story в фазе 2
