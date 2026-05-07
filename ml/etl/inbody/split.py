"""Train/val/test split без leakage по anon_user_id — REQ-18 + SC-05.

Один пользователь → одна часть. Это критично: если строки одного человека
размазать по train и val, валидация будет мерить переобучение на конкретные
индивидуальные тренды, а не обобщающую способность модели.

Алгоритм:
1. Собираем уникальные anon_user_id, сортируем для стабильности.
2. random.Random(seed).shuffle (детерминированно).
3. Берём 70% в train, 15% в val, 15% в test (округление в test для остатка).
4. Помечаем каждую строку соответствующим split-полем.
"""

from __future__ import annotations

import random
from collections.abc import Iterable

from .synthesize import WeekRow

DEFAULT_SPLIT = (0.70, 0.15, 0.15)


def split_users(
    user_ids: Iterable[str],
    *,
    ratios: tuple[float, float, float] = DEFAULT_SPLIT,
    seed: int,
) -> dict[str, str]:
    """Возвращает mapping anon_user_id → 'train' | 'val' | 'test'."""
    if abs(sum(ratios) - 1.0) > 1e-6:
        raise ValueError(f"ratios must sum to 1.0, got {sum(ratios)}")

    unique = sorted(set(user_ids))
    rng = random.Random(seed)
    rng.shuffle(unique)

    n = len(unique)
    n_train = int(n * ratios[0])
    n_val = int(n * ratios[1])
    # Остаток уходит в test — гарантирует, что разделение полное.
    train = unique[:n_train]
    val = unique[n_train : n_train + n_val]
    test = unique[n_train + n_val :]

    mapping: dict[str, str] = {}
    for u in train:
        mapping[u] = "train"
    for u in val:
        mapping[u] = "val"
    for u in test:
        mapping[u] = "test"
    return mapping


def assign_split(
    rows: list[WeekRow], *, seed: int
) -> list[tuple[WeekRow, str]]:
    """Связать каждую строку с её split-меткой.

    Возвращаем list[tuple] — это позволяет writer'у сохранить порядок
    появления и не плодить лишние allocations внутри WeekRow (она
    остаётся «чистой» структурой, не знающей про split).
    """
    user_ids = [r.anon_user_id for r in rows]
    mapping = split_users(user_ids, seed=seed)
    return [(r, mapping[r.anon_user_id]) for r in rows]


def assert_no_leakage(
    rows: list[tuple[WeekRow, str]],
) -> None:
    """SC-05 — invariant assertion. Падаем, если один user в нескольких частях.

    Используется в тестах и опционально перед записью датасета на диск.
    """
    seen: dict[str, str] = {}
    for row, split in rows:
        prev = seen.get(row.anon_user_id)
        if prev is not None and prev != split:
            raise AssertionError(
                f"user {row.anon_user_id} leaked across splits: "
                f"{prev} vs {split}"
            )
        seen[row.anon_user_id] = split
