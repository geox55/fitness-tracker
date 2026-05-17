# InBody-предиктор: сравнение моделей

**Spec:** [008-ai-inbody-predictor.md](../../specs/008-ai-inbody-predictor.md), §2.
**Dataset:** Dataset-B `inbody_timeseries`, см. [012-ml-dataset.md](../../specs/012-ml-dataset.md).

Snapshot воспроизводимый: `make ml-train ML_VERSION=0.1.0` после
`make ml-dataset` на Kaggle-источниках S3 + S4. Команда обучает все
четыре модели (persistence / ridge / lgbm / mlp) и печатает сводную
таблицу через `make ml-compare`.

---

## 1. Источники и размер датасета

| Источник | Описание | Лицензия | Anchor'ов после фильтрации |
|----------|----------|----------|----------------------------|
| Kaggle S3: `valakhorasani/gym-members-exercise-dataset` | 973 строки фитнес-клиентов: пол, возраст, рост, вес, % жира, частота тренировок | См. `ml/data/processed/LICENSES.md` | ~973 |
| Kaggle S4: `fedesoriano/body-fat-prediction-dataset`    | 251 строка с body composition (только мужчины) | — | ~251 |

После prevalence-фильтрации, импутации BMR и синтеза 8-недельных
траекторий ([spec 012 §16](../../specs/012-ml-dataset.md)) — **9776 строк
для 1222 анонимизированных пользователей**. `is_synthetic=True` для всех
строк MVP-датасета (метка для будущего слияния с реальными траекториями).

Сплит train/val/test = 70/15/15 без leakage по `anon_user_id`.
SHA-256 датасета фиксируется в `manifest.json` каждой обученной модели —
если CSV перегенерируется на других источниках, hash меняется и можно
сразу заметить, что модели обучены на другом распределении.

---

## 2. Постановка задачи

Time-series регрессия: на вход — снапшот пользователя в неделю `t`, на
выход — изменение трёх InBody-метрик до недели `t+1`:

```
y_w = weight_kg(t+1) − weight_kg(t)
y_f = body_fat_percent(t+1) − body_fat_percent(t)
y_m = muscle_mass_kg(t+1) − muscle_mass_kg(t)
```

Предсказываем **дельту**, а не абсолютное значение — иначе модель учится
«переписывать вход в выход» и ловит persistence-эффект (для time-series
с малой амплитудой это распространённая ловушка).

Multi-horizon (1/2/4 недели) получается **рекурсивным применением**
one-step-модели: `state_{t+1} = state_t + Δ̂_t`, после чего фичи
пересчитываются заново. CI-bands складываются кумулятивно из q10/q90
квантилей.

---

## 3. Фичи (12 признаков)

| Признак | Тип | Источник |
|---------|-----|----------|
| `age` | int | anchor.age_years |
| `sex_male` | binary | anchor.sex == "male" |
| `height_cm` | float | anchor.height_cm |
| `weight_kg` | float | state.weight_kg (на t) |
| `body_fat_percent` | float | state.body_fat_percent (на t) |
| `muscle_mass_kg` | float \| NaN | state.muscle_mass_kg (на t) |
| `bmi` | float | weight / (height/100)² |
| `ffm` | float | weight · (1 − bf/100) |
| `training_volume_t` | float | trainings_last_8w / 8 |
| `calories_t` | float | actual_calories \|\| target \|\| 2400 |
| `goal_weight_loss` | binary | inferred from per-user mean Δw |
| `goal_muscle_gain` | binary | inferred from per-user mean Δw |

`bmi`/`ffm` детерминированно выводятся из weight_kg + остального — но они
полезны для дерева (явные нелинейности) и для линейной модели как
композитные фичи. `muscle_mass_kg` может быть NaN: LightGBM работает с
пропусками нативно, Ridge получает медиану-импутер.

---

## 4. Сравнение моделей

| модель        | target                 | MAE     | RMSE    | R²      | CI80    |
|---------------|------------------------|---------|---------|---------|---------|
| persistence   | delta_weight_kg        | 0.3249  | 0.3989  | −0.132  | —       |
| persistence   | delta_body_fat_percent | 0.2760  | 0.3468  | −0.150  | —       |
| persistence   | delta_muscle_mass_kg   | 0.1456  | 0.1810  | −0.183  | —       |
| ridge         | delta_weight_kg        | 0.1678  | 0.2102  | 0.686   | —       |
| ridge         | delta_body_fat_percent | 0.2429  | 0.3067  | 0.100   | —       |
| ridge         | delta_muscle_mass_kg   | 0.1267  | 0.1566  | 0.114   | —       |
| **lgbm**      | **delta_weight_kg**    | **0.1555** | **0.1961** | **0.727** | **0.79** |
| **lgbm**      | **delta_body_fat_percent** | **0.2407** | **0.3035** | **0.119** | **0.78** |
| **lgbm**      | **delta_muscle_mass_kg**   | **0.1199** | **0.1477** | **0.212** | **0.80** |
| mlp           | delta_weight_kg        | 0.1561  | 0.1960  | 0.727   | 0.83    |
| mlp           | delta_body_fat_percent | 0.2384  | 0.3009  | 0.134   | 0.79    |
| mlp           | delta_muscle_mass_kg   | 0.1207  | 0.1490  | 0.198   | 0.83    |

**Наблюдения:**

1. **Persistence-baseline разгромлен** на всех таргетах: R² отрицательный
   (модель «всё останется как есть» хуже, чем предсказание среднего по
   обучающей выборке). Это sanity-check — наши признаки несут полезный
   сигнал.

2. **LGBM выигрывает у Ridge на всех трёх дельтах**:
   - `delta_weight_kg`: MAE −7% (0.156 vs 0.168), R² 0.73 vs 0.69;
   - `delta_body_fat`: practically tied (0.241 vs 0.243) — для жира
     процессов с нелинейностями оказывается мало;
   - `delta_muscle_mass`: MAE −5%, R² 0.21 vs 0.11 — у мышечной массы
     нелинейная зависимость от тренировочного объёма проявляется
     отчётливо, и LGBM её ловит.

3. **CI80 coverage 0.78–0.80** — LGBM-quantile-модель **калиброванная**:
   фактический процент попаданий тестовых точек в [q10, q90] совпадает
   с теоретическими 80%. Это критично для UI (REQ-01 spec 008): полоса
   прогноза, которую видит пользователь, действительно содержит истину
   с заявленной частотой.

4. **MLP-квантильная нейросеть vs LGBM** — два разных архитектурных
   подхода с практически идентичной точностью по точечному прогнозу
   (q50): MAE/RMSE отличаются в третьем знаке (например, weight: 0.1561
   vs 0.1555). На body_fat MLP даже чуть лучше по R² (0.134 vs 0.119) —
   shared-trunk multi-task регуляризация помогает на самом «шумном»
   таргете. Это ожидаемая картина для табличных данных малой размерности
   (9776 строк, 12 фичей): GBDT и MLP сходятся к близкой к оптимальной
   аппроксимации, и архитектурный выигрыш почти исчезает (Shwartz-Ziv &
   Armon, 2022). Преимущество выбора в пользу LGBM в проде — скорость
   инференса и интерпретируемость (feature importance из коробки).

5. **CI80 у MLP 0.79–0.83 vs у LGBM 0.78–0.80** — оба варианта
   калиброваны. У MLP coverage слегка превышает теоретические 80%
   (out-of-the-box без conformal-калибровки), что объясняется
   δ-параметризацией: `q10 = q50 − softplus(δ_lower)`,
   `q90 = q50 + softplus(δ_upper)` гарантирует
   `q10 ≤ q50 ≤ q90` по построению, исключая crossing (известную
   проблему независимых quantile-регрессий). Цена — лёгкая
   over-coverage, которую при необходимости можно снять conformal
   prediction'ом на отдельном calibration-сете.

---

## 5. Гиперпараметры основной модели (LGBM)

```python
objective = "quantile"   # alpha = 0.10 / 0.50 / 0.90
metric = "quantile"
learning_rate = 0.05
num_leaves = 15
min_data_in_leaf = 20
feature_fraction = 0.9
bagging_fraction = 0.9
bagging_freq = 5
num_boost_round = 500    # с early_stopping_rounds = 30 на val
random_state = 42
```

Подбирались под малую выборку: `num_leaves=15` (≈глубина 4) — компромисс
между выразительностью и переобучением, `min_data_in_leaf=20` исключает
листья из 1–2 точек, `learning_rate=0.05` достаточно мал, чтобы
early_stopping успевал реагировать.

Воспроизводимость — `random_state=42` фиксирован, ETL-датасет
детерминирован при том же seed (см. [spec 012 REQ-20](../../specs/012-ml-dataset.md)).

## 5a. Гиперпараметры альтернативной модели (MLP)

```python
# Архитектура (PyTorch)
shared_trunk_hidden = (64, 32)   # ReLU + Dropout(0.30)
per_target_head_hidden = 16      # ReLU → 3 выхода (q50, δ_lower, δ_upper)
dropout = 0.30
# q10 = q50 − softplus(δ_lower); q90 = q50 + softplus(δ_upper)

# Обучение
loss = "pinball"                 # сумма по 3 target × 3 quantile, mask NaN
optimizer = "Adam"
learning_rate = 1e-3
weight_decay = 1e-4
batch_size = 256
max_epochs = 200
early_stopping_patience = 20     # по val pinball loss
seed = 42                        # torch + numpy
device = "mps"                   # Apple Silicon; auto-fallback на cuda/cpu
```

Архитектурные решения:

- **Shared trunk + per-target heads** — multi-task learning: общий
  «ствол» извлекает фичи, полезные для всех трёх таргетов (BMI/FFM
  одинаково важны для веса/жира/мышечной), что регуляризует модель в
  условиях малой выборки.
- **δ-параметризация квантилей** — гарантирует упорядоченность
  `q10 ≤ q50 ≤ q90` по построению через `softplus(·) > 0`. Альтернатива
  (три независимые сети на квантиль) даёт crossing на 5–15% точек.
- **Pinball loss с маскированием NaN** — `muscle_mass_kg` может быть
  NaN в anchor-строках (S3-источник не содержит мышечную массу).
  Маскирование исключает такие ячейки из подсчёта loss, не теряя
  всю строку.
- **Гиперпараметры меньше, чем у workout-MLP** (64/32 vs 128/64,
  dropout 0.30 vs 0.30, patience 20 vs 5) — потому что обучающая
  выборка на два порядка меньше (~3k train vs ~80k train), и большая
  сеть быстро переобучается.

---

## 6. Сценарий выкатки

`src/app/domain/forecast/ml_predictor.py`:

1. `load_predictor()` — lazy при первом запросе forecast'а после старта
   API. Ищет последнюю версию в `ml/models/inbody_pred/lgbm/`, читает
   manifest, грузит 9 boosters (3 target × 3 quantile) через `joblib`.
2. В `domains/forecast/service._run_predictor`: если модель загружена
   и `len(history) >= 4` → `build_ml_forecast`; иначе или при любой
   ошибке — fallback к baseline OLS (REQ-12 spec 008). `confidence`
   вычисляется по тем же правилам snapshot'а, не зависит от модели.

После `make ml-train` следующий рестарт API подхватит новую версию
автоматически — никаких изменений в сервисе не требуется.

---

## 7. Что улучшать в дипломе дальше

- **LSTM/Temporal Fusion** — для последовательностей >12 недель
  (синтетика 8 недель пока не оправдывает рекуррентность).
- **Recursive-evaluation метрики** — сейчас MAE/RMSE/R² посчитаны на
  one-step-задаче. Для horizons 2/4 недели нужно отдельно мерить
  `recursive_MAE_h` (накопление ошибки рекурсивным применением).
- **Online-evaluation в проде** — подключить таблицу `ForecastEvaluation`
  (она уже существует со spec 008) для накопления реальных пар «прогноз
  vs факт» и сравнения ML vs baseline на живых пользователях.
- **Feature importance + SHAP** — диагностика модели для главы «Анализ
  результатов» в магистерской работе.
