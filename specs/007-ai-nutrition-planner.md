# Specification: AI планировщик питания

**Epic:** E5 — Питание
**User Story:** Пользователь должен получать персонализированный план питания: суточную калорийность, БЖУ и примерное меню на 7 дней, с учётом цели, веса, BMR и аллергий.
**Related specs:** [002-user-profile.md](002-user-profile.md), [003-inbody-measurements.md](003-inbody-measurements.md), [009-plan-adaptation-and-chat.md](009-plan-adaptation-and-chat.md)

---

## 1. User Goal

Пользователь не хочет считать калории и БЖУ вручную. Он указал цель и аллергии — он хочет получить готовый план: «вот твоя норма, вот примерное меню на неделю». Этот план должен пересматриваться при изменении веса.

В отличие от [006](006-ai-workout-generator.md), здесь **не требуется собственная ML-модель** (по решению команды) — это rule-based блок с детерминированными формулами + опционально LLM (OpenAI API) для генерации текста меню.

---

## 2. Context

Подход к реализации:
1. **Расчёты калорий и БЖУ** — формулы Mifflin-St Jeor + activity multiplier + goal adjustment. Чисто детерминированно.
2. **Генерация меню на 7 дней** — выбор блюд из встроенной базы с учётом БЖУ, аллергий и предпочтений; либо LLM-промпт с шаблоном.

Эта спека покрывает обе задачи. ML здесь не используется (зафиксировано в overview, открытый вопрос).

---

## 3. User Scenarios

### Scenario 1 — Расчёт суточной калорийности и БЖУ

**How to test independently**: Создать пользователя с заполненным профилем + 1 InBody, нажать «Сгенерировать план питания», проверить расчёт.

**Acceptance criteria**:

1. **Given** профиль с полями (sex, birth_date, height_cm, baseline_weight_kg или последний InBody.weight_kg) + цель + частота тренировок.
   **When** пользователь запрашивает план питания.
   **Then** рассчитывается:
   - BMR (Mifflin-St Jeor)
   - TDEE = BMR × activity_multiplier (по training_frequency: 2 → 1.375, 3-4 → 1.55, 5-6 → 1.725)
   - target_calories = TDEE + goal_adjustment (weight_loss: −15%, maintenance: 0, muscle_gain: +10%)
   - белки: 1.6–2.2 г/кг массы (нижняя для maintenance, верхняя для muscle_gain), вес берётся из последнего InBody или baseline
   - жиры: 0.8–1.2 г/кг массы
   - углеводы: остаток калорий

2. **Given** значения посчитаны.
   **When** ответ отображается.
   **Then** видно: target_calories (kcal/день), БЖУ (граммы и %), TDEE, BMR, обоснование (короткий текст).

### Scenario 2 — Генерация меню на 7 дней

**How to test independently**: Запросить меню, проверить структуру (7 дней × 3-5 приёмов пищи) и попадание в БЖУ ±10%.

**Acceptance criteria**:

1. **Given** target_calories и БЖУ рассчитаны.
   **When** генерируется меню.
   **Then** для каждого из 7 дней возвращается список приёмов пищи (завтрак, обед, ужин + 1-2 перекуса) с блюдами, граммовкой, калориями и БЖУ.

2. **Given** суммирование калорий по дню.
   **When** проверяется попадание в норму.
   **Then** дневная сумма ∈ [target_calories × 0.9, target_calories × 1.1], БЖУ ∈ ±15% от целей.

3. **Given** в профиле указаны аллергии (`["gluten", "lactose"]`).
   **When** меню генерируется.
   **Then** ни одно блюдо не содержит этих аллергенов; в карточке блюда есть список аллергенов.

4. **Given** в профиле указано вегетарианство (если поле добавлено в фазе 2).
   **When** меню генерируется.
   **Then** все блюда без мяса/рыбы (если веган — без молочки/яиц).

### Scenario 3 — Замена блюда

Пользователю не нравится конкретное блюдо.

**Acceptance criteria**:

1. **Given** пользователь смотрит меню на день.
   **When** он нажимает «Заменить» на блюде.
   **Then** предлагается альтернатива из той же группы (по БЖУ ±10%) и без аллергенов; пользователь подтверждает.

### Scenario 4 — Адаптация плана при изменении веса

См. [009-plan-adaptation-and-chat.md](009-plan-adaptation-and-chat.md).

**Acceptance criteria**:

1. **Given** изменение веса >2 кг с момента последней генерации плана питания.
   **When** срабатывает фоновый watcher.
   **Then** target_calories пересчитываются автоматически; пользователю приходит уведомление.

### Scenario 5 — Просмотр питательного плана

**Acceptance criteria**:

1. **Given** план питания активен.
   **When** пользователь открывает раздел «Питание».
   **Then** видит: target_calories/БЖУ, текущий день меню, переключение по дням 1..7.

2. **Given** на сегодняшнюю дату нет активного плана.
   **When** пользователь открывает раздел.
   **Then** видит CTA «Сгенерировать план питания».

---

## 4. Functional Requirements

| #      | Requirement                                                                                                |
|--------|------------------------------------------------------------------------------------------------------------|
| REQ-01 | Расчёт BMR по Mifflin-St Jeor                                                                              |
| REQ-02 | Расчёт TDEE с activity multiplier по `training_frequency`                                                  |
| REQ-03 | Расчёт target_calories с adjustment по `goal`                                                              |
| REQ-04 | Расчёт целевых БЖУ (граммы и проценты)                                                                     |
| REQ-05 | Генерация меню на 7 дней с разбивкой по приёмам пищи (3 основных + 1-2 перекуса)                          |
| REQ-06 | Каждый день меню попадает в ±10% по калориям, ±15% по БЖУ от целей                                         |
| REQ-07 | Учёт аллергий: исключение блюд с указанными аллергенами                                                    |
| REQ-08 | Замена блюда вручную (поиск альтернативы по БЖУ ±10%)                                                       |
| REQ-09 | Карточка блюда: название, граммовка, калории, БЖУ, ингредиенты, аллергены, опционально способ приготовления |
| REQ-10 | Только один активный план питания на пользователя; старые архивируются                                      |
| REQ-11 | Источник данных о блюдах: внутренняя БД с минимум 200 блюд + опционально LLM-обогащение                    |
| REQ-12 | Fallback: при недоступности LLM генерация работает на чистой rule-based логике + базе блюд                  |

---

## 5. Non-functional Requirements

| #      | Requirement                                                            | Category    |
|--------|------------------------------------------------------------------------|-------------|
| NFR-01 | Расчёт калорий/БЖУ ≤200 ms                                              | Performance |
| NFR-02 | Генерация меню (rule-based path) ≤3 секунд                              | Performance |
| NFR-03 | Генерация меню (LLM path, если используется) ≤15 секунд + caching       | Performance |
| NFR-04 | Все блюда из БД должны иметь верифицированные значения БЖУ              | Data quality |

---

## 6. Data Model

**Entity: NutritionPlan**

| Field             | Type      | Constraints                              | Description                                |
|-------------------|-----------|------------------------------------------|--------------------------------------------|
| id                | UUID      | PK                                       |                                            |
| user_id           | UUID      | FK → User, required                      |                                            |
| status            | Enum      | `active` \| `archived`                   | Только один active на user                 |
| generated_at      | Timestamp | Required, immutable                      |                                            |
| target_calories   | Integer   | Required, 800..6000                      |                                            |
| protein_g         | Integer   | Required                                 |                                            |
| fat_g             | Integer   | Required                                 |                                            |
| carbs_g           | Integer   | Required                                 |                                            |
| bmr_kcal          | Integer   | Required                                 | Снапшот                                    |
| tdee_kcal         | Integer   | Required                                 |                                            |
| input_features    | JSON      | Required                                 |                                            |
| generation_method | Enum      | `rule_based` \| `llm`                    |                                            |

**Entity: NutritionDay**

| Field    | Type    | Constraints                              | Description                  |
|----------|---------|------------------------------------------|------------------------------|
| id       | UUID    | PK                                       |                              |
| plan_id  | UUID    | FK → NutritionPlan, required             |                              |
| day_no   | Integer | Required, 1..7                           |                              |
| total_calories | Integer | Required                          | Сумма по приёмам             |

**Entity: Meal**

| Field        | Type    | Constraints                                                   | Description                       |
|--------------|---------|---------------------------------------------------------------|-----------------------------------|
| id           | UUID    | PK                                                            |                                   |
| day_id       | UUID    | FK → NutritionDay, required                                   |                                   |
| meal_type    | Enum    | `breakfast` \| `lunch` \| `dinner` \| `snack`                 |                                   |
| order_no     | Integer | Required                                                      | Порядок в дне                     |
| dish_id      | UUID    | FK → Dish, required                                           |                                   |
| servings_g   | Number  | Required, 50..1000                                            | Граммовка порции                  |

**Entity: Dish** (reference data)

| Field          | Type     | Constraints                                                     | Description                                      |
|----------------|----------|-----------------------------------------------------------------|--------------------------------------------------|
| id             | UUID     | PK                                                              |                                                  |
| name           | String   | Required                                                        |                                                  |
| name_ru        | String   | Optional                                                        |                                                  |
| calories_per_100g | Number | Required                                                       |                                                  |
| protein_per_100g | Number | Required                                                        |                                                  |
| fat_per_100g   | Number   | Required                                                        |                                                  |
| carbs_per_100g | Number   | Required                                                        |                                                  |
| allergens      | Enum[]   | Optional                                                        | `gluten`, `lactose`, `nuts`, `eggs`, `fish`, ... |
| ingredients    | String[] | Optional                                                        |                                                  |
| recipe         | Text     | Optional                                                        |                                                  |
| dish_type      | Enum     | `breakfast` \| `lunch` \| `dinner` \| `snack` \| `any`         |                                                  |

---

## 7. Screens

### Screen: Питание (главный)

**Elements**:
- Шапка: target_calories + БЖУ
- Прогресс на сегодня (если интеграция фиксирует фактическое потребление — out of scope в MVP)
- Меню на сегодня: карточки приёмов пищи
- Переключатель «День 1..7»
- Кнопка «Заменить блюдо»
- Меню «...»: «Сгенерировать заново», «Параметры расчёта»

### Screen: Карточка блюда

**Elements**: название, фото (если есть), КБЖУ на порцию, ингредиенты, аллергены, способ приготовления.

### Screen: Замена блюда

**Elements**: список 3-5 альтернатив с БЖУ, кнопка «Выбрать».

---

## 9. API Endpoints

### Сгенерировать план питания

```
POST /api/v1/nutrition/plans/generate
```

**Response 201**:
```json
{
  "plan_id": "uuid",
  "target_calories": 2400,
  "protein_g": 180,
  "fat_g": 70,
  "carbs_g": 260,
  "bmr_kcal": 1750,
  "tdee_kcal": 2710,
  "generation_method": "rule_based",
  "days": [
    {
      "day_no": 1,
      "total_calories": 2380,
      "meals": [
        {
          "meal_type": "breakfast",
          "dish_id": "uuid",
          "name": "Овсянка с черникой",
          "servings_g": 250,
          "calories": 380,
          "protein_g": 14,
          "fat_g": 8,
          "carbs_g": 60,
          "allergens": []
        }
      ]
    }
  ]
}
```

### Получить активный план

```
GET /api/v1/nutrition/plans/active
```

### Заменить блюдо

```
POST /api/v1/nutrition/meals/{meal_id}/replace
```
**Response 200**: новый Meal + список потенциальных альтернатив.

### Поиск альтернатив

```
GET /api/v1/nutrition/dishes/alternatives?dish_id=...&exclude_allergens=gluten,lactose
```

---

## 10. Edge Cases

- Профиль без InBody → используется baseline_weight_kg из профиля.
- Цель `weight_loss` + очень низкий BMR → не уходить ниже 1200 ккал для женщин и 1500 для мужчин (медицинская граница).
- Все блюда из БД исключены аллергиями → возвращается ошибка `no_dishes_match` с понятной формулировкой.
- LLM-сервис недоступен → fallback на чистый rule-based (помечается в `generation_method`).
- Пользователь живёт без интернета → последний план кешируется на клиенте.

---

## 11. Out of Scope

- Учёт фактического потребления (food log) — отдельный эпик
- Сканирование штрих-кодов / распознавание еды по фото
- Свой ML для подбора меню (зафиксировано: только rule-based + опционально LLM)
- Список покупок на неделю — отдельная story
- Интеграция со службами доставки еды
- Учёт микронутриентов (витамины, минералы)
- Расчёт для детей / беременных / медицинские диеты
