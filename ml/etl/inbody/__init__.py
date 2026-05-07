"""ETL для Dataset-B inbody_timeseries — spec 012 §2.

Структура (см. spec §9):
- `sources.py` — парсеры raw CSV (Kaggle S3 = gym-members-exercise-dataset,
  S4 = body-fat-prediction-dataset) → общий формат `Anchor`.
- `impute.py` — Mifflin-St Jeor BMR (REQ-14) + outlier-фильтры (Edge case §10).
- `synthesize.py` — синтезатор недельных траекторий вокруг anchor (REQ-16).
  Это главный научный кусок Маши: алгоритм описан в коде и в магистерской.
- `anonymize.py` — sha256(salt) хеш и random-offset дат (REQ-17, NFR-03).
- `split.py` — 70/15/15 без leakage по anon_user_id (REQ-18, SC-05).
- `build.py` — entry point: связывает всё в pipeline.
- `cli.py` — argparse-обёртка.
"""
