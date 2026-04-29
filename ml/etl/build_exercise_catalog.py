"""Скачивает free-exercise-db и нормализует под нашу схему `exercises`.

Источник: https://github.com/yuhonas/free-exercise-db (MIT, ~870 упражнений).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "yuhonas/free-exercise-db/main/dist/exercises.json"
)

# free-exercise-db muscle name → наш enum
_MUSCLE_MAP: dict[str, str] = {
    "abdominals": "abs",
    "abductors": "glutes",
    "adductors": "quads",
    "biceps": "biceps",
    "calves": "calves",
    "chest": "chest",
    "forearms": "forearms",
    "glutes": "glutes",
    "hamstrings": "hamstrings",
    "lats": "lats",
    "lower back": "lower_back",
    "middle back": "back",
    "neck": "back",
    "quadriceps": "quads",
    "shoulders": "shoulders",
    "traps": "traps",
    "triceps": "triceps",
}

# free-exercise-db equipment → наш enum
_EQUIPMENT_MAP: dict[str, str] = {
    "barbell": "barbell",
    "bands": "resistance_band",
    "body only": "bodyweight",
    "cable": "cable",
    "dumbbell": "dumbbell",
    "e-z curl bar": "barbell",
    "exercise ball": "other",
    "foam roll": "other",
    "kettlebells": "kettlebell",
    "machine": "machine",
    "medicine ball": "medicine_ball",
    "other": "other",
}

_UPPER_BODY = {
    "chest", "back", "shoulders", "biceps", "triceps", "forearms",
    "lats", "traps", "lower_back",
}
_LOWER_BODY = {"quads", "hamstrings", "glutes", "calves"}
_CORE = {"abs", "obliques"}


def _slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    if not s:
        s = "ex_" + hashlib.sha1(name.encode()).hexdigest()[:8]
    return s


def _body_region(primary: str) -> str:
    if primary in _UPPER_BODY:
        return "upper"
    if primary in _LOWER_BODY:
        return "lower"
    if primary in _CORE:
        return "core"
    return "full_body"


def _normalize_one(raw: dict[str, Any]) -> dict[str, Any] | None:
    name = raw.get("name")
    primaries = raw.get("primaryMuscles") or []
    if not name or not primaries:
        return None

    primary = _MUSCLE_MAP.get(primaries[0].lower())
    if primary is None:
        return None

    secondary = sorted(
        {
            _MUSCLE_MAP[m.lower()]
            for m in (raw.get("secondaryMuscles") or [])
            if m.lower() in _MUSCLE_MAP
        }
    )

    eq_raw = (raw.get("equipment") or "").lower()
    equipment = [_EQUIPMENT_MAP.get(eq_raw, "other")]

    instructions = "\n".join(raw.get("instructions") or [])
    body_region = _body_region(primary)
    slug = _slugify(name)

    return {
        "exercise_id": slug,
        "exercise_name": name,
        "exercise_name_ru": None,
        "primary_muscle_group": primary,
        "secondary_muscle_group": secondary,
        "instructions": instructions,
        "equipment": equipment,
        "body_region": body_region,
    }


def fetch_source(url: str = SOURCE_URL) -> list[dict[str, Any]]:
    req = urllib.request.Request(url, headers={"User-Agent": "fitness-tracker-etl"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for entry in raw:
        norm = _normalize_one(entry)
        if norm is None:
            continue
        # дедуп по slug — если уже есть с длиннее instructions, оставляем
        existing = seen.get(norm["exercise_id"])
        if existing is None or len(norm["instructions"]) > len(existing["instructions"]):
            seen[norm["exercise_id"]] = norm
    items = sorted(seen.values(), key=lambda x: x["exercise_name"])
    return items


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build normalized exercises catalog.")
    p.add_argument("--out", required=True, help="Путь к выходному JSON")
    p.add_argument("--source", default=SOURCE_URL, help="URL исходного JSON")
    args = p.parse_args(argv)

    print(f"-> downloading {args.source}", file=sys.stderr)
    raw = fetch_source(args.source)
    print(f"   raw entries: {len(raw)}", file=sys.stderr)

    items = build(raw)
    print(f"-> normalized: {len(items)} unique exercises", file=sys.stderr)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"-> wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
