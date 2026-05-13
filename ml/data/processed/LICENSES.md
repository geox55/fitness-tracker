# Лицензии источников Dataset-B

Этот документ — справка для воспроизведения сборки. Реальные raw-файлы
**не коммитятся в репозиторий** — их нужно скачать вручную с Kaggle.

---

## S3 — gym-members-exercise-dataset

- **URL:** https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset
- **Автор:** Vala Khorasani
- **Лицензия (на момент 2026-05):** CC0 1.0 (Public Domain)
- **Файл, который мы используем:** `gym_members_exercise_tracking.csv`
  (положить в `ml/data/raw/gym_members_exercise.csv`)
- **Колонки, которые мы читаем:** Age, Gender, Weight (kg), Height (m),
  Session_Duration (hours), Fat_Percentage, Workout_Frequency (days/week),
  Experience_Level.

CC0 разрешает любое использование, включая коммерческое, без указания
авторства. Мы всё равно ссылаемся на источник в магистерской работе.

---

## S4 — body-fat-prediction-dataset

- **URL:** https://www.kaggle.com/datasets/fedesoriano/body-fat-prediction-dataset
- **Автор:** fedesoriano
- **Лицензия (на момент 2026-05):** CC0 1.0
- **Файл:** `bodyfat.csv` (положить как `ml/data/raw/bodyfat.csv`)
- **Колонки:** Age, Weight (lb), Height (in), BodyFat (%).
- **Контингент:** только мужчины — это смещение учтено в dataset_card.md.

---

## Перепроверка

Перед публикацией модели/датасета в магистерской: ещё раз свериться со
страницами Kaggle — лицензии иногда меняются авторами. Если хотя бы один
источник окажется не CC0/MIT/CC-BY-4.0 — заменяем альтернативой и
пересобираем pipeline.
