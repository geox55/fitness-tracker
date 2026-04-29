"""Перевод английских названий упражнений на русский по правилам.

Подход: ищем в названии ключевые слова в порядке приоритета (movement,
position, equipment, body-part) и собираем строку по фиксированному шаблону:

    [Movement] [Position] [BodyPart] [Equipment] [Variant]

Если самого главного — movement — найти не удалось, отдаём None и UI
покажет английское название (fallback в PWA уже сделан).

Цель — быстрый baseline без внешних зависимостей. ~70% качество.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --- словари ---------------------------------------------------------------

# Ключевое движение — определяет шаблон. Порядок важен (более длинные первыми).
_MOVEMENTS: list[tuple[str, str]] = [
    ("bench press", "Жим лёжа"),
    ("overhead press", "Жим стоя"),
    ("shoulder press", "Жим плечами"),
    ("military press", "Армейский жим"),
    ("incline press", "Жим на наклонной"),
    ("decline press", "Жим на наклонной обратной"),
    ("push press", "Швунг"),
    ("push-up", "Отжимания"),
    ("push up", "Отжимания"),
    ("pull-up", "Подтягивания"),
    ("pull up", "Подтягивания"),
    ("chin-up", "Подтягивания обратным хватом"),
    ("chin up", "Подтягивания обратным хватом"),
    ("pulldown", "Тяга вертикального блока"),
    ("pulldowns", "Тяга вертикального блока"),
    ("pull-down", "Тяга вертикального блока"),
    ("row", "Тяга"),
    ("rows", "Тяга"),
    ("deadlift", "Становая тяга"),
    ("deadlifts", "Становая тяга"),
    ("squat", "Приседания"),
    ("squats", "Приседания"),
    ("lunge", "Выпад"),
    ("lunges", "Выпады"),
    ("step-up", "Зашагивания"),
    ("step up", "Зашагивания"),
    ("crunch", "Скручивания"),
    ("crunches", "Скручивания"),
    ("sit-up", "Подъём корпуса"),
    ("sit up", "Подъём корпуса"),
    ("leg raise", "Подъём ног"),
    ("leg raises", "Подъём ног"),
    ("knee raise", "Подъём коленей"),
    ("knee raises", "Подъём коленей"),
    ("calf raise", "Подъём на носки"),
    ("calf raises", "Подъём на носки"),
    ("lateral raise", "Махи в стороны"),
    ("lateral raises", "Махи в стороны"),
    ("front raise", "Махи перед собой"),
    ("front raises", "Махи перед собой"),
    ("rear delt fly", "Махи в наклоне"),
    ("rear delt flies", "Махи в наклоне"),
    ("reverse fly", "Махи в наклоне"),
    ("reverse flies", "Махи в наклоне"),
    ("fly", "Разведение"),
    ("flies", "Разведение"),
    ("flyes", "Разведение"),
    ("curl", "Сгибание"),
    ("curls", "Сгибание"),
    ("extension", "Разгибание"),
    ("extensions", "Разгибание"),
    ("kickback", "Отведение"),
    ("kickbacks", "Отведение"),
    ("shrug", "Шраги"),
    ("shrugs", "Шраги"),
    ("dip", "Отжимания на брусьях"),
    ("dips", "Отжимания на брусьях"),
    ("plank", "Планка"),
    ("hyperextension", "Гиперэкстензия"),
    ("hyperextensions", "Гиперэкстензия"),
    ("good morning", "Наклоны со штангой"),
    ("good mornings", "Наклоны со штангой"),
    ("clean", "Взятие на грудь"),
    ("clean and jerk", "Толчок"),
    ("snatch", "Рывок"),
    ("swing", "Махи"),
    ("swings", "Махи"),
    ("twist", "Скручивания корпусом"),
    ("twists", "Скручивания корпусом"),
    ("thruster", "Трастер"),
    ("burpee", "Бёрпи"),
    ("burpees", "Бёрпи"),
    ("running", "Бег"),
    ("walking", "Ходьба"),
    ("cycling", "Велосипед"),
    ("rowing", "Гребля"),
    ("press", "Жим"),
    ("raise", "Подъём"),
    ("raises", "Подъём"),
    ("pull", "Тяга"),
    ("pullover", "Пуловер"),
    ("pullovers", "Пуловер"),
    ("crossover", "Кроссовер"),
    ("crossovers", "Кроссовер"),
    ("hold", "Удержание"),
    ("holds", "Удержание"),
]

# Положение тела — добавляется после движения.
_POSITIONS: dict[str, str] = {
    "standing": "стоя",
    "seated": "сидя",
    "sitting": "сидя",
    "lying": "лёжа",
    "kneeling": "на коленях",
    "incline": "на наклонной",
    "decline": "на наклонной обратной",
    "flat": "горизонтальный",
    "bent-over": "в наклоне",
    "bent over": "в наклоне",
    "single-leg": "на одной ноге",
    "single leg": "на одной ноге",
    "single-arm": "одной рукой",
    "single arm": "одной рукой",
    "one-arm": "одной рукой",
    "one arm": "одной рукой",
    "alternating": "попеременно",
    "wide-grip": "широким хватом",
    "wide grip": "широким хватом",
    "close-grip": "узким хватом",
    "close grip": "узким хватом",
    "neutral-grip": "нейтральным хватом",
    "neutral grip": "нейтральным хватом",
    "reverse-grip": "обратным хватом",
    "reverse grip": "обратным хватом",
}

# Оборудование — приставка с предлогом.
_EQUIPMENT: dict[str, str] = {
    "barbell": "со штангой",
    "dumbbell": "с гантелями",
    "dumbbells": "с гантелями",
    "kettlebell": "с гирей",
    "kettlebells": "с гирями",
    "cable": "на блоке",
    "machine": "в тренажёре",
    "smith machine": "в Смите",
    "trap bar": "с трэп-грифом",
    "ez-bar": "с EZ-грифом",
    "ez bar": "с EZ-грифом",
    "e-z bar": "с EZ-грифом",
    "e-z curl bar": "с EZ-грифом",
    "resistance band": "с резинкой",
    "resistance bands": "с резинкой",
    "band": "с резинкой",
    "bands": "с резинкой",
    "medicine ball": "с медболом",
    "exercise ball": "на фитболе",
    "stability ball": "на фитболе",
    "bosu ball": "на босу",
    "trx": "с TRX",
    "weighted": "с весом",
    "bodyweight": "с собственным весом",
    "body weight": "с собственным весом",
    "body-weight": "с собственным весом",
    "chair": "со стулом",
    "bench": "на скамье",
    "wall": "у стены",
    "rope": "с канатом",
    "chains": "с цепями",
}

# Часть тела — обычно идёт после движения как уточнение.
_BODY: dict[str, str] = {
    "chest": "груди",
    "back": "спины",
    "shoulder": "плеча",
    "shoulders": "плеч",
    "tricep": "трицепса",
    "triceps": "трицепса",
    "bicep": "бицепса",
    "biceps": "бицепса",
    "leg": "ноги",
    "legs": "ног",
    "hip": "бедра",
    "hips": "бёдер",
    "ab": "пресса",
    "abs": "пресса",
    "abdominal": "пресса",
    "abdominals": "пресса",
    "lat": "широчайших",
    "lats": "широчайших",
    "trap": "трапеции",
    "traps": "трапеций",
    "glute": "ягодиц",
    "glutes": "ягодиц",
    "calf": "икр",
    "calves": "икр",
    "forearm": "предплечья",
    "forearms": "предплечий",
    "neck": "шеи",
    "wrist": "запястья",
    "ankle": "лодыжки",
    "hamstring": "бедра",
    "hamstrings": "бицепса бедра",
    "quad": "квадрицепса",
    "quads": "квадрицепса",
    "core": "кора",
    "oblique": "косых",
    "obliques": "косых",
}


# --- алгоритм --------------------------------------------------------------

_word_re = re.compile(r"[a-z]+(?:[-' ][a-z]+)*", re.IGNORECASE)


def _find_movement(low: str) -> tuple[str, int, int] | None:
    for key, value in _MOVEMENTS:
        idx = low.find(key)
        if idx != -1:
            return value, idx, idx + len(key)
    return None


def _find_first_match(low: str, mapping: dict[str, str]) -> str | None:
    # Сначала длинные ключи (single-arm > arm).
    keys = sorted(mapping, key=len, reverse=True)
    for k in keys:
        if k in low:
            return mapping[k]
    return None


def translate(name: str) -> str | None:
    low = name.lower()

    movement = _find_movement(low)
    if movement is None:
        return None
    movement_ru = movement[0]

    position = _find_first_match(low, _POSITIONS)
    equipment = _find_first_match(low, _EQUIPMENT)
    body = _find_first_match(low, _BODY)

    parts: list[str] = [movement_ru]
    # «Жим лёжа» уже содержит position, не дублируем.
    if position and position not in movement_ru.lower():
        parts.append(position)
    if body and body not in movement_ru.lower():
        parts.append(body)
    if equipment:
        parts.append(equipment)

    result = " ".join(p for p in parts if p)
    # Капитализуем только первую букву.
    return result[0].upper() + result[1:] if result else None


# --- CLI -------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Annotate exercises_catalog.json with Russian names.")
    p.add_argument("input", help="входной JSON от build_exercise_catalog.py")
    p.add_argument("--out", required=True, help="выходной JSON")
    args = p.parse_args(argv)

    items: list[dict[str, object]] = json.loads(Path(args.input).read_text("utf-8"))
    translated = 0
    for item in items:
        existing = item.get("exercise_name_ru")
        if existing:
            translated += 1
            continue
        name = item["exercise_name"]
        ru = translate(str(name))
        if ru:
            item["exercise_name_ru"] = ru
            translated += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    pct = round(translated / max(len(items), 1) * 100)
    print(f"-> translated {translated}/{len(items)} ({pct}%)", file=sys.stderr)
    print(f"-> wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
