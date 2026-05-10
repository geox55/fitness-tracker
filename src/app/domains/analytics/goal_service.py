"""Прогресс по цели — БД-обвязка для spec 010 §3 Scenario 3 (REQ-05).

Сервис собирает воедино:
- профиль (goal, target_weight_kg, target_muscle_kg, goal_started_at,
  baseline_weight_kg) — REQ-06;
- последний и стартовый InBody-замеры пользователя;
- прогноз ([008](008-ai-inbody-predictor.md)) для расчёта ETA.

Чистые формулы (compute_progress / compute_eta) — в `domain.analytics`.
Здесь только I/O и склейка.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.analytics import EtaConfidence, GoalKind, compute_eta, compute_progress
from ..forecast.service import NotEnoughInBodyError, get_forecast
from ..inbody.models import InBodyMeasurement
from ..profile.models import UserProfile

NoGoalReason = Literal[
    "no_goal_in_profile",  # goal=None или maintenance
    "no_target_set",  # target_*_kg не указан для выбранной цели
    "no_inbody_measurements",  # нет ни одного замера для start_value
]


@dataclass(frozen=True)
class GoalProgress:
    """Положительный сценарий: прогресс есть и считается.

    `eta` может быть None даже при known goal+target — если прогноз не
    построился (мало данных) или цель ещё далеко за горизонтом прогноза.
    `eta_confidence` берём из forecast bundle.confidence (low/medium/high).
    """

    goal: GoalKind
    start_value: float
    current_value: float
    target_value: float
    progress_percent: int
    already_reached: bool
    eta: date | None
    eta_confidence: EtaConfidence | None
    started_at: date


@dataclass(frozen=True)
class NoGoal:
    """Empty-state: пользователь увидит CTA «Укажите цель в профиле»."""

    reason: NoGoalReason
    # Какие именно поля профиля надо заполнить — UI подставит в сообщение.
    missing_fields: tuple[str, ...]


GoalProgressResult = GoalProgress | NoGoal


def _pick_metric(goal: GoalKind) -> str:
    return "weight_kg" if goal == "weight_loss" else "muscle_mass_kg"


def _pick_target(profile: UserProfile, goal: GoalKind) -> float | None:
    raw = (
        profile.target_weight_kg
        if goal == "weight_loss"
        else profile.target_muscle_kg
    )
    return float(raw) if raw is not None else None


def _read_metric(m: InBodyMeasurement, metric: str) -> float | None:
    value = getattr(m, metric, None)
    return float(value) if value is not None else None


async def _load_history(
    session: AsyncSession, *, user_id: uuid.UUID
) -> list[InBodyMeasurement]:
    """Все замеры пользователя в хронологическом порядке."""
    stmt = (
        select(InBodyMeasurement)
        .where(InBodyMeasurement.user_id == user_id)
        .order_by(InBodyMeasurement.measured_at.asc())
    )
    return list((await session.execute(stmt)).scalars().all())


def _resolve_start(
    *,
    history: list[InBodyMeasurement],
    profile: UserProfile,
    goal: GoalKind,
    metric: str,
) -> tuple[float, date] | None:
    """Найти стартовое значение метрики и дату старта.

    Приоритет источника:
    1) первый замер в/после `goal_started_at` (если та задана) — мы хотим
       прогресс **с момента, когда начали работать над целью**, а не с
       первого ever-замера;
    2) первый замер истории — fallback, если started_at не задан;
    3) для weight_loss дополнительно `baseline_weight_kg` из профиля,
       если в первом замере вес отсутствует (не должно быть, т.к. вес —
       обязательное поле, но защищаемся).

    Возвращает None, если ни одного значения собрать не удалось.
    """
    started_at = profile.goal_started_at
    candidates = history
    if started_at is not None:
        # >= started_at; .date() даёт naive-сравнение, что нам подходит:
        # измерения с datetime на ту же дату — уже "после старта".
        candidates = [m for m in history if m.measured_at.date() >= started_at]
        if not candidates:
            # started_at есть, но замеров после неё нет — ждём первого
            # замера, прогресс пока не показываем.
            return None

    for m in candidates:
        v = _read_metric(m, metric)
        if v is not None:
            resolved_started = started_at or m.measured_at.date()
            return v, resolved_started

    # Ни одного замера с заполненной метрикой. Для weight_loss подстрахуемся
    # baseline'ом из профиля.
    if goal == "weight_loss" and profile.baseline_weight_kg is not None:
        baseline_date = (
            started_at
            or (history[0].measured_at.date() if history else date.today())
        )
        return float(profile.baseline_weight_kg), baseline_date
    return None


def _resolve_current(
    history: list[InBodyMeasurement], metric: str
) -> tuple[float, datetime] | None:
    """Последний замер пользователя с заполненной метрикой."""
    for m in reversed(history):
        v = _read_metric(m, metric)
        if v is not None:
            return v, m.measured_at
    return None


async def get_goal_progress(
    session: AsyncSession, *, user_id: uuid.UUID
) -> GoalProgressResult:
    """Главная точка входа сервиса. Возвращает либо `GoalProgress`,
    либо `NoGoal` с причиной — API мапит на 200 с разными payload'ами.
    """
    profile = await session.get(UserProfile, user_id)
    if profile is None or profile.goal is None or profile.goal == "maintenance":
        # maintenance = нет «достижимой» цифры; UX тот же, что без цели.
        return NoGoal(
            reason="no_goal_in_profile",
            missing_fields=("goal",),
        )

    goal: GoalKind = profile.goal
    target = _pick_target(profile, goal)
    if target is None:
        target_field = (
            "target_weight_kg" if goal == "weight_loss" else "target_muscle_kg"
        )
        return NoGoal(reason="no_target_set", missing_fields=(target_field,))

    metric = _pick_metric(goal)
    history = await _load_history(session, user_id=user_id)
    if not history:
        return NoGoal(
            reason="no_inbody_measurements", missing_fields=("inbody_measurements",)
        )

    start = _resolve_start(history=history, profile=profile, goal=goal, metric=metric)
    current = _resolve_current(history, metric)
    if start is None or current is None:
        # Например, у юзера есть замеры, но без muscle_mass_kg, а цель —
        # muscle_gain. Считаем как «недостаточно данных для прогресса».
        return NoGoal(
            reason="no_inbody_measurements", missing_fields=(metric,)
        )

    start_value, started_at = start
    current_value, _current_at = current
    calc = compute_progress(
        start_value=start_value,
        current_value=current_value,
        target_value=target,
        goal=goal,
    )

    eta, eta_confidence = await _resolve_eta(
        session, user_id=user_id, target=target, goal=goal
    )

    return GoalProgress(
        goal=goal,
        start_value=start_value,
        current_value=current_value,
        target_value=target,
        progress_percent=calc.progress_percent,
        already_reached=calc.already_reached,
        eta=eta,
        eta_confidence=eta_confidence,
        started_at=started_at,
    )


async def _resolve_eta(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    target: float,
    goal: GoalKind,
) -> tuple[date | None, EtaConfidence | None]:
    """Достать ForecastBundle и спроецировать пересечение target в дату.

    Возвращает (None, None), если прогноз не построился (NotEnoughInBoyError):
    UI просто не покажет ETA, прогресс-бар при этом отрисуется как раньше.
    """
    try:
        bundle, _generated, based_on_id = await get_forecast(
            session, user_id=user_id
        )
    except NotEnoughInBodyError:
        return None, None

    series = bundle.weight_kg if goal == "weight_loss" else bundle.muscle_mass_kg
    anchor = await session.get(InBodyMeasurement, based_on_id)
    if anchor is None:
        return None, None

    # ForecastPoint совпадает по форме с ForecastSample (Protocol) — duck-typed.
    eta = compute_eta(
        points=series.points,
        target_value=target,
        goal=goal,
        anchor_date=anchor.measured_at.date(),
    )
    return eta, bundle.confidence
