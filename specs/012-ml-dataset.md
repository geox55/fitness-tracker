# Specification: ML Dataset — объединение источников

**Epic:** E8 — Данные и ML-инфраструктура
**User Story:** Команда должна иметь два рабочих датасета — справочник упражнений и обучающий набор для ML-моделей — собранных из публичных источников и приведённых к единой схеме.
**Related specs:** [004-exercise-catalog.md](004-exercise-catalog.md), [006-ai-workout-generator.md](006-ai-workout-generator.md), [008-ai-inbody-predictor.md](008-ai-inbody-predictor.md)

---

## 1. User Goal

«Пользователь» здесь — сама команда (ML-разработчики). Им нужно из набора публичных датасетов собрать два рабочих набора:

- **Datasets-A — Exercise Catalog**: справочник упражнений, который заливается в БД и используется в [004](004-exercise-catalog.md) и как пул выбора в AI-генераторе ([006](006-ai-workout-generator.md)).
- **Datasets-B — User-trajectory training set**: тренировочный набор для ML-моделей ([006](006-ai-workout-generator.md), [008](008-ai-inbody-predictor.md)) — фичи пользователя + InBody-замеры + (где есть) упражнения и результаты.

ETL должен быть воспроизводимым: один и тот же пайплайн → один и тот же выход.

---

## 2. Context

Источники, перечисленные командой:

| ID  | Source                                                                                  | Что внутри                                              | Используется в  |
|-----|-----------------------------------------------------------------------------------------|---------------------------------------------------------|-----------------|
| S1  | https://www.kaggle.com/datasets/ambarishdeb/gym-exercises-dataset                        | Упражнения с описанием, оборудованием                   | A               |
| S2  | https://www.kaggle.com/datasets/omarxadel/fitness-exercises-dataset                      | Упражнения, инструкции                                  | A               |
| S3  | https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset              | Профили клиентов зала: возраст, пол, BMI, частота, длительность тренировок, тип упражнения | B   |
| S4  | https://www.kaggle.com/datasets/fedesoriano/body-fat-prediction-dataset                  | Рост, вес, замеры тела → % жира                         | B               |
| API | https://api-ninjas.com/api/exercises                                                     | Упражнения с инструкциями, типом, оборудованием         | A               |

Лицензии источников проверяются перед публикацией модели/приложения (см. open question — добавится в overview).

Целевые поля **A (exercises)** — из ТЗ:
`exercise_id, exercise_name, primary_muscle_group, secondary_muscle_group, instructions, equipment, calories_burned_per_hour, body_region`.

Целевые поля **B (training set)** — производные от моделей:
- Для workout-generator: фичи пользователя (sex, age, height, weight, body_fat, muscle_mass, BMR, goal, level, frequency, equipment_available) + label (рекомендуемое упражнение/сплит). Поскольку прямого labeled-датасета нет, формируется через **rule-based авто-разметку** (это явная часть scope).
- Для inbody-predictor: timeline пользователя (фичи по неделям) + следующее значение InBody. Источники: S3 + S4 + синтетика на основе статистики.

---

## 3. User Scenarios

### Scenario 1 — Сборка Dataset-A (Exercise Catalog)

**How to test independently**: Запустить `etl/build_exercise_catalog.py`, проверить выход — единый CSV/parquet с N строк и заявленной схемой.

**Acceptance criteria**:

1. **Given** установлены raw-файлы S1, S2 и API ключ для S(api-ninjas).
   **When** запускается ETL.
   **Then** генерируется единый файл `dataset_a_exercises.parquet` с колонками `exercise_id, exercise_name, primary_muscle_group, secondary_muscle_group, instructions, equipment, calories_burned_per_hour, body_region, source_dataset, exercise_name_ru?` и ≥500 строк.

2. **Given** одно и то же упражнение (например «Barbell Bench Press») присутствует в S1 и S(api).
   **When** запускается дедупликация.
   **Then** остаётся одна запись; источник — `merged`; недостающие поля из одного источника дособираются из другого.

3. **Given** в исходниках разные значения muscle_group (`pectorals`, `chest`, `Chest`).
   **When** проходит нормализация.
   **Then** все приводятся к контролируемому enum из [004](004-exercise-catalog.md).

4. **Given** в исходниках отсутствует поле `calories_burned_per_hour`.
   **When** ETL обогащает данные.
   **Then** значение проставляется по таблице эталонных оценок (из публичных MET-таблиц) или null с пометкой.

5. **Given** часть инструкций только на английском.
   **When** ETL формирует файл.
   **Then** для топ-200 самых частых упражнений добавляется перевод `exercise_name_ru` (через предзаполненный словарь, не автомашперевод).

### Scenario 2 — Сборка Dataset-B (Training set)

**How to test independently**: Запустить `etl/build_training_set.py`, проверить наличие двух выходов: для workout-recommender и для inbody-predictor.

**Acceptance criteria**:

1. **Given** установлены raw-файлы S3, S4.
   **When** запускается ETL.
   **Then** генерируются два набора:
   - `dataset_b_workout_recsys.parquet` — `(user_features, recommended_exercise_id, weight)` для рекомендательной модели; разметка получена rule-based (правила генерации см. в магистерской работе Егора).
   - `dataset_b_inbody_timeseries.parquet` — `(user_features_t, target_inbody_t+τ)` для time-series регрессии; формируется из S3 (длинные серии тренировок) и/или из синтетики на S4.

2. **Given** в S3 нет поля BMR.
   **When** ETL обогащает фичи.
   **Then** BMR вычисляется по Mifflin-St Jeor из age, sex, height, weight.

3. **Given** S4 — кросс-секционные данные (без time-series).
   **When** формируется timeseries-набор.
   **Then** строится синтетика: для каждого условного «пользователя» из S3 моделируется траектория в окрестности его параметров на горизонте 4-8 недель (с шумом). Алгоритм синтеза описывается в коде ETL и в магистерской.

4. **Given** PII (имена, точные даты, конкретные айдентификаторы) могут попасть в training set.
   **When** проходит ETL.
   **Then** все идентификаторы хэшируются (sha256 + project salt), даты сдвигаются (random offset на пользователя), сохраняется только относительный delta.

### Scenario 3 — Сидинг каталога в БД

**How to test independently**: Запустить `seed/seed_exercises.py` против пустой БД, убедиться что `exercises` table заполнен и работают эндпоинты [004](004-exercise-catalog.md).

**Acceptance criteria**:

1. **Given** есть `dataset_a_exercises.parquet`.
   **When** запускается сид.
   **Then** все строки вставляются в таблицу `exercises` идемпотентно (повторный запуск не создаёт дубликатов; обновляет изменившиеся записи по `exercise_id`).

### Scenario 4 — Версионирование датасетов

**Acceptance criteria**:

1. **Given** ETL запущен с конкретной версией скриптов и raw-файлов.
   **When** генерируется выход.
   **Then** в файле есть `dataset_version`, `built_at`, `source_files_hashes`.

2. **Given** запущен с тем же входом.
   **When** ETL прошёл.
   **Then** выход bit-for-bit идентичен (в пределах детерминизма pandas/parquet).

---

## 4. Functional Requirements

### Dataset-A (Exercise Catalog)

| #      | Requirement                                                                                              |
|--------|----------------------------------------------------------------------------------------------------------|
| REQ-01 | Парсинг S1, S2 в pandas DataFrame с известной схемой                                                     |
| REQ-02 | Парсинг API Ninjas с пагинацией и rate limiting                                                           |
| REQ-03 | Нормализация: muscle_group, equipment, body_region — приведение к enum из [004](004-exercise-catalog.md) |
| REQ-04 | Дедупликация по нормализованному `exercise_name` (lowercase, без знаков препинания)                       |
| REQ-05 | Генерация стабильного `exercise_id` (slug на основе name)                                                  |
| REQ-06 | Заполнение `calories_burned_per_hour` из MET-таблиц или null                                             |
| REQ-07 | Заполнение `body_region` (upper/lower/core/full_body) на основе primary_muscle_group                      |
| REQ-08 | Перевод названий топ-200 упражнений на русский через предзаполненный словарь                              |
| REQ-09 | Выход: parquet + JSON-схема + report (count rows, missing fields stats)                                   |
| REQ-10 | Идемпотентный seed-скрипт для БД                                                                         |
| REQ-11 | Лицензионная справка по каждому источнику (LICENSES.md в папке датасета)                                 |

### Dataset-B (Training Set)

| #      | Requirement                                                                                              |
|--------|----------------------------------------------------------------------------------------------------------|
| REQ-12 | Парсинг S3 — пользовательские профили + сессии тренировок                                                  |
| REQ-13 | Парсинг S4 — body composition                                                                            |
| REQ-14 | Имputation BMR через Mifflin-St Jeor                                                                      |
| REQ-15 | Rule-based авторазметка для workout-recsys (правила фиксированы в коде, описание в магистерской)         |
| REQ-16 | Синтетика временных рядов InBody вокруг S4 + фичей S3                                                     |
| REQ-17 | Анонимизация: hash идентификаторов, рандомное смещение дат                                                |
| REQ-18 | Train/val/test split 70/15/15 с фиксированным seed                                                         |
| REQ-19 | Выход: parquet + dataset_card.md (что есть, как собрано, какие смещения и ограничения)                   |
| REQ-20 | Все ETL-скрипты воспроизводимы (фиксированные версии библиотек, sha256 raw-файлов в логе)                 |

---

## 5. Non-functional Requirements

| #      | Requirement                                                                              | Category     |
|--------|------------------------------------------------------------------------------------------|--------------|
| NFR-01 | ETL для Dataset-A прогоняется ≤5 минут на ноутбуке                                        | DX           |
| NFR-02 | ETL для Dataset-B (включая синтетику) ≤30 минут                                           | DX           |
| NFR-03 | Никакие реальные PII не попадают в публикуемые артефакты                                  | Privacy      |
| NFR-04 | Лицензии всех публичных датасетов совместимы с использованием в учебном/публичном проекте | Compliance   |

---

## 6. Success Criteria

| #     | Criterion                                                                  | How to measure                                          |
|-------|----------------------------------------------------------------------------|---------------------------------------------------------|
| SC-01 | В каталоге ≥500 уникальных упражнений с заполненными ≥6 из 8 полей         | Скрипт-валидатор отчёта                                 |
| SC-02 | Покрытие enum-ов: ≥10 muscle_groups, ≥8 equipment, 4 body_regions          | Statistics из ETL отчёта                                |
| SC-03 | В Dataset-B inbody_timeseries ≥1000 пользовательских траекторий (4+ точек) | Counts на выходе                                         |
| SC-04 | Рубрики `dataset_card.md` заполнены: source, license, biases, limitations  | Линт                                                     |
| SC-05 | Train/val/test разделение не имеет утечки (один пользователь → одна часть) | Тест на пересечения в split-скрипте                     |

---

## 7. Data Model

(Артефакты хранятся в репозитории, не в БД, кроме сидинга каталога.)

**Output: dataset_a_exercises.parquet**

| Field                    | Type     | Required | Source                          |
|--------------------------|----------|----------|---------------------------------|
| exercise_id              | string   | yes      | derived (slug)                  |
| exercise_name            | string   | yes      | merged                           |
| exercise_name_ru         | string   | optional | dictionary                       |
| primary_muscle_group     | enum     | yes      | normalized                       |
| secondary_muscle_group   | enum[]   | optional |                                 |
| instructions             | text     | yes      | longest from sources             |
| equipment                | enum[]   | yes      | normalized                       |
| calories_burned_per_hour | float    | optional | MET table                        |
| body_region              | enum     | yes      | derived from primary_muscle_group|
| source_dataset           | string   | yes      | tracking                         |

**Output: dataset_b_workout_recsys.parquet**

| Field                  | Type    | Required | Description                                  |
|------------------------|---------|----------|----------------------------------------------|
| anon_user_id           | string  | yes      | hashed                                       |
| sex                    | enum    | yes      |                                              |
| age                    | int     | yes      |                                              |
| height_cm              | float   | yes      |                                              |
| weight_kg              | float   | yes      |                                              |
| body_fat_percent       | float   | optional |                                              |
| muscle_mass_kg         | float   | optional |                                              |
| bmr_kcal               | float   | yes      | computed if missing                          |
| goal                   | enum    | yes      |                                              |
| training_level         | enum    | yes      |                                              |
| frequency              | int     | yes      |                                              |
| equipment_available    | enum[]  | yes      |                                              |
| recommended_exercise_id| string  | yes      | rule-based label                             |
| label_weight           | float   | yes      | confidence/priority                          |
| split                  | enum    | yes      | `train` \| `val` \| `test`                   |

**Output: dataset_b_inbody_timeseries.parquet**

| Field                  | Type    | Required | Description                              |
|------------------------|---------|----------|------------------------------------------|
| anon_user_id           | string  | yes      |                                          |
| t_week                 | int     | yes      | неделя относительно baseline             |
| age                    | int     | yes      |                                          |
| sex                    | enum    | yes      |                                          |
| height_cm              | float   | yes      |                                          |
| weight_kg              | float   | yes      | текущее значение на неделю t             |
| body_fat_percent       | float   | yes      |                                          |
| muscle_mass_kg         | float   | optional |                                          |
| training_volume_t      | float   | yes      | агрегат тренировок за неделю             |
| calories_t             | float   | optional |                                          |
| target_weight_t1       | float   | yes      | label: вес на t+1                         |
| target_bf_t1           | float   | yes      |                                          |
| target_mm_t1           | float   | optional |                                          |
| split                  | enum    | yes      |                                          |
| is_synthetic           | bool    | yes      | true для синтезированных строк           |

---

## 9. Артефакты репозитория (вместо API)

```
ml/
  data/
    raw/                          (gitignored, описано в README)
    processed/
      dataset_a_exercises.parquet
      dataset_b_workout_recsys.parquet
      dataset_b_inbody_timeseries.parquet
      dataset_card.md
      LICENSES.md
  etl/
    build_exercise_catalog.py
    build_training_set.py
    normalize.py
    synthesize_timeseries.py
  seed/
    seed_exercises.py
```

Команды:
```
uv run python ml/etl/build_exercise_catalog.py --out ml/data/processed/
uv run python ml/etl/build_training_set.py --out ml/data/processed/
uv run python ml/seed/seed_exercises.py --db $DATABASE_URL
```

---

## 10. Edge Cases

- API Ninjas вернул 429 (rate limit) → ретраи с экспоненциальным бэкоффом, при исчерпании — fallback на кэшированную копию.
- Один из Kaggle-датасетов недоступен → ETL падает с явной ошибкой, не подделывает данные.
- Дублирование упражнения с разными значениями `instructions` → выбирается самая длинная (предполагаем, более информативная); ссылки на оба источника сохраняются.
- В S3 экстремальные значения BMI (<10 или >70) → отбрасываются как outliers.
- Пользователь с <2 точками в timeseries-наборе → исключается из обучающей выборки (не хватает динамики).

---

## 11. Out of Scope

- Online дообучение моделей — отдельный эпик
- Сбор реальных пользовательских данных (это будет happen-after-launch, отдельная privacy-история)
- Автоматическая интеграция с внешними API (Apple Health, Garmin) для расширения данных
- Качественные оценки данных через экспертов-тренеров (валидация рекомендаций упражнений)
- ML feature store
- Видео/изображения упражнений в датасете
- Перевод инструкций на русский для всех 500+ упражнений (только топ-200 названий) — фаза 2
