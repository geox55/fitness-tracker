# Workout-recommender: сравнение моделей

**Spec:** [006-ai-workout-generator.md](../../specs/006-ai-workout-generator.md), §2.
**Dataset:** Dataset-C `workout_recommender` (ETL: `ml.etl.workout_recommender`).

Snapshot воспроизводимый: `make ml-rec-train` после
`make ml-rec-dataset` на тех же Kaggle-источниках S3 + S4 (что и для
InBody-предиктора), плюс exercises_catalog.json (Dataset-A).

---

## 1. Постановка задачи

Бинарная классификация: на вход — пара `(user, exercise)`, на выход —
скор «релевантно ли упражнение пользователю?». Recommender ранжирует
весь каталог по скору, top-K попадает в день тренировки. Финальный план
на 4 недели собирает rule-based composer (балансирует группы мышц,
прогрессирует нагрузку) поверх ML-ranking'а — это гибридная схема,
явно описанная в spec 006 §2.

ML-ответственность здесь — не «составить тренировку», а «отделить
релевантные упражнения от нерелевантных». Composer собирать день/неделю
из top-K — детерминированная задача, и держать её в ML смысла нет
(меньше решений → меньше тестов и меньше рисков).

---

## 2. Источник меток (rule-based labelling)

Прямой labeled-датасета «правильное упражнение для этого пользователя»
в открытом доступе нет. Метки формируются эвристикой
(`ml/etl/workout_recommender/labelling.py`):

```
relevance(user, exercise) =
    w_goal · goal_match
    + w_level · level_match
    + w_region · region_match
    + w_balance · balance_match
    − exclusion_by_equipment
```

- `goal_match`: 1.0 если primary_muscle_group ∈ priority(goal); 0.5 если
  это secondary group; 0.0 иначе.
- `level_match`: beginner отрезает «advanced-only» движения (snatch,
  clean, pistol, и т.п.); intermediate допускает их с весом 0.5;
  advanced — всё.
- `region_match`: бонус за совпадение body_region с приоритетным регионом
  (weight_loss → lower+core; muscle_gain → upper+lower; и т.д.).
- `balance_match`: бонус за компаунды (упражнения с secondary group).
- `equipment exclusion`: жёстко 0, если нужно оборудование вне
  `equipment_available` пользователя — REQ-06 spec 006.

Бинаризация: `label = score >= 1.5`. На полном Dataset-C получается
**67.5% positives** — class balance подходит для binary classification
с `is_unbalance=True` в LGBM (или `class_weight='balanced'` в LR).

Эта эвристика — **не финальная модель**, а training signal: она задаёт,
что́ считать «правильным», а ML ловит non-linear сочетания (advanced ×
muscle_gain × chest → benchpress сильнее squat).

---

## 3. Размер и сплит датасета

| Источник | Anchor'ов |
|----------|-----------|
| Kaggle S3 (gym_members_exercise) | 973 |
| Kaggle S4 (bodyfat) | 251 |

После filter+impute → 1222 анонимизированных user'а.
Каталог упражнений (Dataset-A) — 873 строки.
На каждого user'а сэмплим 80 упражнений (rng seed=42) → **97 760 пар**.

Из них:
- 65 995 (67.5%) — positives;
- 23 483 — excluded by equipment (label=0 жёстко).

Сплит train/val/test = 70/15/15 **без leakage по anon_user_id**.

---

## 4. Сравнение моделей

| модель      | ROC-AUC | PR-AUC | Precision@8 | Recall@8 |
|-------------|---------|--------|-------------|----------|
| popularity  | 0.500   | 0.679  | 0.689       | 0.104    |
| LogisticRegression | 0.939 | 0.964 | 0.952      | 0.232    |
| **LightGBM**  | **0.985** | **0.993** | **0.990** | **0.241** |

**Наблюдения:**

1. **Popularity-baseline ROC-AUC=0.500** — sanity: predict_constant даёт
   именно случайное упорядочивание. Precision@K=0.69 = baseline-rate
   positives, как ожидается. Любая модель выше этой строки полезна.

2. **LR vs LGBM**: LR уже даёт 0.939 ROC-AUC — labelling-эвристика по
   значительной части линейна (one-hot goal × group дают ясный сигнал).
   LGBM забирает оставшиеся 4.6pp ROC-AUC за счёт нелинейностей
   (advanced × beginner, equipment_count × needs_barbell, и т.п.).

3. **Precision@8 = 0.990** для LGBM: из 8 рекомендованных упражнений в
   среднем 7.92 — релевантные. Это критично для UX: top-8 идёт в день
   плана как кандидат-пул, composer выбирает оттуда баланс групп.

4. **Recall@8 = 0.24** — низкий, но это свойство задачи: positives
   ~67% от каталога (≈580 упражнений на user'а в среднем), 8 — это
   ~1.4% от positives. Recall@K не максимизируется — мы хотим топ
   качества, а не покрытие.

---

## 5. Гиперпараметры основной модели (LightGBM)

```python
objective = "binary"
metric = "binary_logloss"
learning_rate = 0.05
num_leaves = 31
min_data_in_leaf = 50
feature_fraction = 0.9
bagging_fraction = 0.9
bagging_freq = 5
is_unbalance = True
num_boost_round = 600    # с early_stopping_rounds = 30 на val
random_state = 42
```

`min_data_in_leaf=50` — защита от листьев из 1 пользователя
(no-leakage по группам уже на CV-уровне через split, но дополнительная
гарантия не повредит).

---

## 6. Сценарий выкатки (планируется)

`src/app/domain/workout_generator/recommender.py` (TODO в следующей итерации):

1. `load_recommender()` — lazy-load LightGBM-артефакта
   (`ml/models/workout_rec/lgbm/v0.1.0/lgbm.joblib`) и manifest.
2. `score(user_features, exercise_features) -> probability`.
3. Композитор `build_plan(user, profile, frequency)`:
   - top-K=10..16 (зависит от частоты тренировок);
   - rule-based распределение по дням (балансирует push/pull/legs,
     не нагружает одну группу два дня подряд);
   - прогрессия 4 недели через Linear Progression (для beginner) или
     Double Progression (intermediate/advanced).
4. Fallback: при любой ошибке инференса — детерминированный rule-based
   из шаблонов (REQ-16).

API: `POST /api/v1/plans/generate` → `WorkoutPlan` с 4 неделями,
структура из spec 006 §9.

---

## 7. Что улучшать дальше

- **Real labels collection**: добавить feedback-loop в проде (был ли
  пользователь готов выполнить рекомендованное упражнение, сколько раз
  фактически сделал) → дообучение на реальных данных вместо synthetic.
- **Personalization beyond rules**: matrix factorization (user-embedding
  × exercise-embedding) — сейчас фичи user'а агрегированы, embeddings
  поймали бы индивидуальные предпочтения.
- **Multi-task**: совместное предсказание (relevance, expected_RPE,
  expected_completion_rate) — даёт композитору больше сигнала.
- **Calibration**: Brier score + Platt scaling — для прогрессии нагрузки
  (target_weight) пригодилась бы калиброванная вероятность, а не ranking.
