"""Чистый детектор «вес заметно изменился» — REQ-01 + Scenario 1.

Триггер срабатывает, если:
- |new − prev| > 2 кг, ИЛИ
- |new − prev| / prev > 3% **И** разница по дате между замерами < 30 дней.

Возвращаем структуру `WeightDelta`, чтобы вызывающий сервис мог сразу
сохранить delta_kg/delta_percent в `PlanRebuildEvent`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

ABS_THRESHOLD_KG = 2.0
REL_THRESHOLD_PCT = 3.0
REL_WINDOW_DAYS = 30


@dataclass(frozen=True)
class WeightDelta:
    delta_kg: float
    delta_percent: float
    days_between: int


def compute_delta(
    *,
    prev_weight_kg: float,
    new_weight_kg: float,
    prev_measured_at: datetime,
    new_measured_at: datetime,
) -> WeightDelta:
    if prev_weight_kg <= 0:
        raise ValueError("prev_weight_kg must be positive")
    delta_kg = new_weight_kg - prev_weight_kg
    delta_percent = (delta_kg / prev_weight_kg) * 100.0
    days_between = (new_measured_at - prev_measured_at).days
    return WeightDelta(
        delta_kg=delta_kg,
        delta_percent=delta_percent,
        days_between=days_between,
    )


def should_trigger(delta: WeightDelta) -> bool:
    """Основное правило (REQ-01).

    Edge case §10: «два InBody подряд за один день — сравниваем с предыдущим
    из другого дня». На уровне service.py: при загрузке prev мы уже отбрасываем
    замеры с тем же днём, что у нового. Здесь же `days_between == 0` означает,
    что вызывающий передал прошлый-разный-день и просто получил ноль —
    в этом случае относительная проверка по 30-дневному окну не сработает,
    останется только абсолютная.
    """
    if abs(delta.delta_kg) > ABS_THRESHOLD_KG:
        return True
    return (
        0 <= delta.days_between < REL_WINDOW_DAYS
        and abs(delta.delta_percent) > REL_THRESHOLD_PCT
    )
