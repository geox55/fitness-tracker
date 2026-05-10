"""Pure-функции для расчёта прогресса по цели — spec 010 §3 Scenario 3, REQ-05.

Сюда едет только арифметика: процент достижения цели + ETA по точкам
прогноза. БД и forecast.service остаются в `domains/analytics`. Это
позволяет писать unit-ы без `AsyncSession`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal, Protocol

GoalKind = Literal["weight_loss", "muscle_gain"]
EtaConfidence = Literal["high", "medium", "low"]


class ForecastSample(Protocol):
    """Duck-typed контракт точки прогноза.

    Структурный тип, чтобы pure-helper'у не нужно было импортировать
    `domain.forecast.ForecastPoint`: тестам можно передавать локальный
    dataclass, сервису — реальный ForecastPoint, оба совпадают по форме.

    Поля заданы через @property, чтобы frozen-dataclass'ы тоже подпадали
    под структурную совместимость (с прямыми атрибутами Protocol требует
    mutable-доступ — frozen dataclass его не предоставляет).
    """

    @property
    def horizon_weeks(self) -> int: ...

    @property
    def point(self) -> float: ...


@dataclass(frozen=True)
class GoalCalc:
    """Результат `compute_progress`.

    `progress_percent` — целое в [0; 100], округлённое (REQ-05): UI рисует
    progress bar ровно по этому числу. Отрицательный «откат» клампим до 0,
    чтобы не пугать пользователя «-3% прогресса»; в карточке ниже всё
    равно видны абсолютные значения, и направление считывается оттуда.

    `already_reached` — True если current уже на/за target. Полезно
    отдельно от 100% — это маркер «пора ставить новую цель».
    """

    progress_percent: int
    already_reached: bool


def compute_progress(
    *,
    start_value: float,
    current_value: float,
    target_value: float,
    goal: GoalKind,
) -> GoalCalc:
    """Сколько от пути «start → target» уже пройдено.

    weight_loss:    progress = (start - current) / (start - target)
    muscle_gain:    progress = (current - start) / (target - start)

    Если `start == target`, считать прогресс нечего — деление на 0; в этом
    случае возвращаем 100% (цель формально совпадает с базовой точкой,
    логично показать «достигнуто»).
    """
    denom = start_value - target_value if goal == "weight_loss" else target_value - start_value
    numer = (
        start_value - current_value
        if goal == "weight_loss"
        else current_value - start_value
    )

    if denom == 0:
        # Пользователь поставил target = start (например, поддержание веса
        # с явной целью weight_loss) — считаем достигнутой по факту записи.
        return GoalCalc(progress_percent=100, already_reached=True)

    raw_pct = numer / denom * 100.0
    clamped = max(0.0, min(100.0, raw_pct))

    # already_reached — отдельная проверка по знаку, чтобы маркер сработал
    # и в случае «перевыполнили» (current уже за target).
    reached = (
        current_value <= target_value
        if goal == "weight_loss"
        else current_value >= target_value
    )
    return GoalCalc(progress_percent=round(clamped), already_reached=reached)


def compute_eta(
    *,
    points: Iterable[ForecastSample],
    target_value: float,
    goal: GoalKind,
    anchor_date: date,
) -> date | None:
    """Дата, на которой forecast пересечёт target.

    Алгоритм:
    - точки прогноза приходят на дискретных горизонтах (1, 2, 4, 8, 12 нед.);
    - идём по соседним парам, ищем первую, между которыми traj пересёк
      target в нужную сторону (вниз для weight_loss, вверх для muscle_gain);
    - линейно интерполируем horizon_weeks до пересечения и переводим в date.

    Возвращает None если:
    - список пустой (forecast не построился — частый случай при <2 замерах);
    - ни одна точка ещё не пересекла target в горизонте прогноза (ETA «после»
      последней точки — не показываем, чтобы не врать о «через 6 месяцев»
      на основе 12-недельного прогноза).
    - target уже достигнут в начальной точке (тогда `already_reached`
      обрабатывает вызывающий код, а ETA не имеет смысла).
    """
    sorted_points = sorted(points, key=lambda p: p.horizon_weeks)
    if not sorted_points:
        return None

    # «Достигнуто» в направлении цели:
    # weight_loss → когда point ≤ target (вес упал до или ниже).
    # muscle_gain → когда point ≥ target.
    def reached(value: float) -> bool:
        return value <= target_value if goal == "weight_loss" else value >= target_value

    # Если самая первая точка прогноза уже за target — возвращаем её дату:
    # цель достижима в пределах ближайшего горизонта, ETA = эта точка.
    first = sorted_points[0]
    if reached(first.point):
        return anchor_date + timedelta(weeks=first.horizon_weeks)

    # Идём по парам и ищем пересечение.
    prev = first
    for nxt in sorted_points[1:]:
        if reached(nxt.point):
            # Линейная интерполяция horizon_weeks между prev и nxt:
            # ищем h, при котором значение = target.
            span_value = nxt.point - prev.point
            if span_value == 0:
                # Параллельная траектория, прыжок ровно через target —
                # возьмём nxt как pessimistic-оценку.
                return anchor_date + timedelta(weeks=nxt.horizon_weeks)
            t = (target_value - prev.point) / span_value
            # t ∈ [0, 1] — гарантировано, т.к. prev не reached, nxt reached.
            t = max(0.0, min(1.0, t))
            interp_weeks = prev.horizon_weeks + t * (
                nxt.horizon_weeks - prev.horizon_weeks
            )
            # Округляем до дня (timedelta(weeks=...) поддерживает float).
            return anchor_date + timedelta(weeks=interp_weeks)
        prev = nxt

    return None  # ETA вне горизонта прогноза
