"""Шаблонные ответы ассистента — REQ-11.

Чистые функции: на вход профиль (anonymized snapshot), на выход — текст.
Никакого I/O, никакого LLM. Всё, что вернётся пользователю, можно ревьюить
по диффу.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserContext:
    """Срез данных пользователя для шаблонов.

    Все поля опциональны — пользователь мог не закончить онбординг. Шаблоны
    обязаны корректно работать даже с пустым контекстом (Edge case: первый
    вход в чат до настройки профиля).
    """

    name: str | None = None
    goal: str | None = None  # weight_loss | muscle_gain | maintenance
    training_level: str | None = None
    training_frequency: int | None = None
    weight_kg: float | None = None
    bmr_kcal: int | None = None


@dataclass(frozen=True)
class TemplateResult:
    text: str
    # Что мы подставили — чтобы service.py сохранил в `context` для
    # отладки/воспроизводимости.
    context: dict[str, object]


_GOAL_RU = {
    "weight_loss": "снижение веса",
    "muscle_gain": "набор массы",
    "maintenance": "поддержание формы",
}


def _greeting(name: str | None) -> str:
    return f"{name}, " if name else ""


def render_why_these_sets(ctx: UserContext) -> TemplateResult:
    if ctx.training_level is None or ctx.goal is None:
        return TemplateResult(
            text=(
                "План подбирается по вашему уровню и цели. Заполните профиль, "
                "и я смогу объяснить подробнее."
            ),
            context={},
        )
    goal_ru = _GOAL_RU.get(ctx.goal, ctx.goal)
    by_level = {
        "beginner": "сначала техника, поэтому 3 подхода по 10–12 повторов",
        "intermediate": "стандартный объём 3–4×8–10 — оптимум для прогресса",
        "advanced": "повышенный объём 4–5×6–10 — двигаем рабочие веса",
    }.get(ctx.training_level, "стандартный объём 3×8–10")
    return TemplateResult(
        text=(
            f"{_greeting(ctx.name)}при цели «{goal_ru}» и уровне "
            f"«{ctx.training_level}» {by_level}. Когда вы стабильно превышаете "
            "целевые повторения, AI поднимет рабочий вес в следующем цикле."
        ),
        context={"goal": ctx.goal, "training_level": ctx.training_level},
    )


def render_what_is_rpe(_ctx: UserContext) -> TemplateResult:
    return TemplateResult(
        text=(
            "RPE (Rate of Perceived Exertion) — субъективная оценка сложности "
            "подхода от 1 до 10. RPE 7 — «осталось 3 повтора в запасе», RPE 9 — "
            "«1 повтор в запасе», RPE 10 — отказ. Используем для дозировки нагрузки."
        ),
        context={},
    )


def render_protein_need(ctx: UserContext) -> TemplateResult:
    if ctx.weight_kg is None or ctx.goal is None:
        return TemplateResult(
            text=(
                "Белок нужен для роста и восстановления мышц. Норма зависит "
                "от вашей цели и веса — заполните профиль, и я посчитаю."
            ),
            context={},
        )
    per_kg = {
        "weight_loss": 1.8,
        "muscle_gain": 2.0,
        "maintenance": 1.4,
    }.get(ctx.goal, 1.4)
    grams = round(ctx.weight_kg * per_kg)
    return TemplateResult(
        text=(
            f"При цели «{_GOAL_RU.get(ctx.goal, ctx.goal)}» и весе "
            f"{ctx.weight_kg:.1f} кг ориентир — около {grams} г белка в день "
            f"({per_kg} г/кг). Это поможет сохранить и нарастить мышцы."
        ),
        context={"goal": ctx.goal, "weight_kg": ctx.weight_kg, "grams": grams},
    )


def render_pre_workout_food(_ctx: UserContext) -> TemplateResult:
    return TemplateResult(
        text=(
            "За 1.5–2 часа до тренировки — медленные углеводы + белок: овсянка "
            "с творогом, рис с курицей, хлеб с яйцом. За 30 минут — банан, "
            "если нужно «дозаправиться». Тяжёлую жирную пищу лучше избегать."
        ),
        context={},
    )


def render_missed_workout(ctx: UserContext) -> TemplateResult:
    if ctx.training_frequency is not None and ctx.training_frequency >= 4:
        suffix = (
            "Пропуск одной тренировки из 4 в неделю не критичен — продолжайте "
            "по графику, ничего навёрстывать не нужно."
        )
    else:
        suffix = (
            "Сдвиньте следующую тренировку на день и продолжайте по плану — "
            "лучше пропустить одну, чем сломать график."
        )
    return TemplateResult(
        text=f"{_greeting(ctx.name)}{suffix}",
        context={"training_frequency": ctx.training_frequency},
    )


def render_rest_days(_ctx: UserContext) -> TemplateResult:
    return TemplateResult(
        text=(
            "Между тренировками одной мышечной группы — 48 часов. Между "
            "разными группами можно тренироваться подряд. Полный день отдыха "
            "1–2 раза в неделю обязателен."
        ),
        context={},
    )


def render_weight_plateau(ctx: UserContext) -> TemplateResult:
    if ctx.goal == "weight_loss":
        text = (
            "Плато при похудении — нормально. Проверьте: не вырос ли средний "
            "рацион незаметно, держится ли дефицит 300–500 ккал, есть ли 2–3 "
            "силовые тренировки в неделю. Если 2+ недели без сдвига — снизьте "
            "ккал на 100 или добавьте кардио."
        )
    elif ctx.goal == "muscle_gain":
        text = (
            "Если вес и силовые не растут 2+ недели — добавьте 150–200 ккал "
            "в день и проверьте, что белок ≥1.8 г/кг."
        )
    else:
        text = (
            "Стабильный вес при цели «поддержание» — это и есть успех. Если "
            "хотите изменить направление, поменяйте цель в профиле."
        )
    return TemplateResult(text=text, context={"goal": ctx.goal})


# Реестр: topic_id → renderer. Сервис чата выбирает функцию по id.
RENDERERS = {
    "why_these_sets": render_why_these_sets,
    "what_is_rpe": render_what_is_rpe,
    "protein_need": render_protein_need,
    "pre_workout_food": render_pre_workout_food,
    "missed_workout": render_missed_workout,
    "rest_days": render_rest_days,
    "weight_plateau": render_weight_plateau,
}


def render_topic(topic_id: str, ctx: UserContext) -> TemplateResult | None:
    fn = RENDERERS.get(topic_id)
    if fn is None:
        return None
    return fn(ctx)
