"""Рекомендации на основе ML-прогноза InBody.

Принимает текущий замер + прогноз ML-модели (ForecastBundle) + цель
пользователя → возвращает персонализированные советы. ML предсказывает
динамику, этот модуль интерпретирует прогноз в конкретные действия.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..forecast.predictor import ForecastBundle


@dataclass(frozen=True)
class MeasurementSnapshot:
    weight_kg: float
    body_fat_percent: float
    sex: str
    muscle_mass_kg: float | None = None
    body_water_percent: float | None = None
    protein_kg: float | None = None
    minerals_kg: float | None = None
    visceral_fat_level: int | None = None


@dataclass(frozen=True)
class Tip:
    icon: str
    title: str
    body: str
    severity: str  # info | warning | success


def generate_tips(
    snapshot: MeasurementSnapshot,
    forecast: ForecastBundle | None,
    goal: str | None,
) -> list[Tip]:
    tips: list[Tip] = []

    if forecast is not None:
        _tips_from_forecast(snapshot, forecast, goal, tips)

    _tips_from_current(snapshot, goal, tips)

    return tips


def _delta_at_horizon(forecast: ForecastBundle, attr: str, weeks: int) -> float | None:
    series = getattr(forecast, attr, None)
    if series is None:
        return None
    for p in series.points:
        if p.horizon_weeks == weeks:
            base = getattr(series, "_base", None)
            return p.point
    return None


def _longest_point(forecast: ForecastBundle, attr: str) -> float | None:
    series = getattr(forecast, attr, None)
    if series is None or not series.points:
        return None
    return series.points[-1].point


def _tips_from_forecast(
    snap: MeasurementSnapshot,
    fc: ForecastBundle,
    goal: str | None,
    tips: list[Tip],
) -> None:
    pred_weight = _longest_point(fc, "weight_kg")
    pred_fat = _longest_point(fc, "body_fat_percent")
    pred_muscle = _longest_point(fc, "muscle_mass_kg")

    horizon = fc.weight_kg.points[-1].horizon_weeks if fc.weight_kg.points else 4

    if pred_weight is not None:
        delta_w = pred_weight - snap.weight_kg
        if goal == "weight_loss" and delta_w > 0.2:
            tips.append(Tip(
                icon="trending_up",
                title="Модель прогнозирует набор веса",
                body=f"По прогнозу вес вырастет на {delta_w:+.1f} кг за {horizon} нед. "
                     "Попробуйте снизить калорийность на 200–300 ккал или "
                     "добавить одну кардиотренировку в неделю.",
                severity="warning",
            ))
        elif goal == "weight_loss" and delta_w < -0.3:
            tips.append(Tip(
                icon="trending_down",
                title="Вес снижается — вы на верном пути",
                body=f"Прогноз: {delta_w:+.1f} кг за {horizon} нед. "
                     "Не снижайте калории слишком резко — "
                     "важно сохранить мышечную массу.",
                severity="success",
            ))
        elif goal == "muscle_gain" and delta_w < -0.2:
            tips.append(Tip(
                icon="trending_down",
                title="Вес падает — мало калорий для набора",
                body=f"Прогноз: {delta_w:+.1f} кг за {horizon} нед. "
                     "Увеличьте калорийность на 300–500 ккал в день, "
                     "добавьте сложные углеводы (крупы, макароны, хлеб).",
                severity="warning",
            ))

    if pred_fat is not None:
        delta_f = pred_fat - snap.body_fat_percent
        if delta_f > 0.5:
            tips.append(Tip(
                icon="monitor_heart",
                title="Процент жира растёт",
                body=f"Прогноз: {delta_f:+.1f}% за {horizon} нед. "
                     "Добавьте 2–3 кардиотренировки в неделю и "
                     "сократите быстрые углеводы (сахар, выпечка).",
                severity="warning",
            ))
        elif goal == "weight_loss" and delta_f < -0.3:
            tips.append(Tip(
                icon="monitor_heart",
                title="Жир уходит — отличная динамика",
                body=f"Прогноз: {delta_f:+.1f}% за {horizon} нед. "
                     "Продолжайте в том же режиме.",
                severity="success",
            ))

    if pred_muscle is not None:
        delta_m = pred_muscle - snap.muscle_mass_kg if snap.muscle_mass_kg else None
        if delta_m is not None:
            if goal == "muscle_gain" and delta_m < 0.1:
                tips.append(Tip(
                    icon="fitness_center",
                    title="Мышцы растут медленно",
                    body=f"Прогноз: {delta_m:+.1f} кг за {horizon} нед. "
                         "Увеличьте белок до 2 г на кг веса и "
                         "добавьте прогрессию нагрузки в тренировках.",
                    severity="warning",
                ))
            elif delta_m > 0.2:
                tips.append(Tip(
                    icon="fitness_center",
                    title="Мышечная масса растёт",
                    body=f"Прогноз: {delta_m:+.1f} кг за {horizon} нед. "
                         "Хороший результат — продолжайте.",
                    severity="success",
                ))
            elif delta_m < -0.2:
                tips.append(Tip(
                    icon="fitness_center",
                    title="Мышцы уходят",
                    body=f"Прогноз: {delta_m:+.1f} кг за {horizon} нед. "
                         "Не сокращайте белок (минимум 1.6 г на кг веса) и "
                         "сохраняйте силовые тренировки даже на дефиците.",
                    severity="warning",
                ))


def _tips_from_current(
    snap: MeasurementSnapshot,
    goal: str | None,
    tips: list[Tip],
) -> None:
    # Нормы InBody: вода 45–65% от веса тела, зависит от мышечной массы.
    # Ниже 45% — обезвоживание, ниже 50% — стоит пить больше.
    if snap.body_water_percent is not None and snap.body_water_percent < 45.0:
        tips.append(Tip(
            icon="water_drop",
            title="Низкий уровень воды в организме",
            body=f"Сейчас {snap.body_water_percent:.1f}%, норма по InBody — 45–65%. "
                 "Пейте не менее 30 мл воды на 1 кг веса в день. "
                 "Ограничьте кофе и алкоголь — они выводят жидкость.",
            severity="warning",
        ))
    elif snap.body_water_percent is not None and snap.body_water_percent < 50.0:
        tips.append(Tip(
            icon="water_drop",
            title="Воды в организме маловато",
            body=f"Сейчас {snap.body_water_percent:.1f}%, желательно от 50%. "
                 "Добавьте 2–3 стакана воды в день, особенно до и после тренировки.",
            severity="info",
        ))

    # Белок: норма InBody ~16% от массы тела. Ниже — мышцы недополучают
    # строительный материал.
    if snap.protein_kg is not None:
        ratio = snap.protein_kg / snap.weight_kg * 100
        if ratio < 14.0:
            tips.append(Tip(
                icon="egg",
                title="Белок значительно ниже нормы",
                body=f"Белок {snap.protein_kg:.1f} кг ({ratio:.1f}% от веса, норма — от 16%). "
                     "Добавьте в каждый приём пищи источник белка: "
                     "мясо, рыбу, яйца, творог или бобовые.",
                severity="warning",
            ))
        elif ratio < 16.0:
            tips.append(Tip(
                icon="egg",
                title="Белок немного ниже нормы",
                body=f"Белок {snap.protein_kg:.1f} кг ({ratio:.1f}% от веса, норма — 16%). "
                     "Перекусывайте орехами, греческим йогуртом "
                     "или протеиновым коктейлем после тренировки.",
                severity="info",
            ))

    # Минералы: норма InBody — 4–6% от массы тела. Это в основном
    # кальций и фосфор в костях.
    if snap.minerals_kg is not None:
        ratio = snap.minerals_kg / snap.weight_kg * 100
        if ratio < 4.0:
            tips.append(Tip(
                icon="science",
                title="Минералов ниже нормы",
                body=f"Минералы {snap.minerals_kg:.1f} кг ({ratio:.1f}% от веса, норма — 4–6%). "
                     "Это в основном кальций в костях. Ешьте молочные продукты "
                     "(творог, сыр, кефир), зелень (шпинат, брокколи) и орехи (миндаль). "
                     "Витамин D помогает усвоению — гуляйте на солнце.",
                severity="warning",
            ))
        elif ratio < 5.0:
            tips.append(Tip(
                icon="science",
                title="Минералы на нижней границе нормы",
                body=f"Минералы {snap.minerals_kg:.1f} кг ({ratio:.1f}% от веса, норма — 4–6%). "
                     "Добавьте в рацион сыр, кунжут, сардины и листовую зелень.",
                severity="info",
            ))

    # Висцеральный жир: InBody рекомендует уровень до 10.
    # 10–15 — повышенный, >15 — высокий риск.
    if snap.visceral_fat_level is not None:
        if snap.visceral_fat_level > 15:
            tips.append(Tip(
                icon="warning",
                title="Висцеральный жир высокий",
                body=f"Уровень {snap.visceral_fat_level} (норма — до 10). "
                     "Это жир вокруг внутренних органов, повышающий риск "
                     "диабета и сердечно-сосудистых заболеваний. "
                     "Помогут: кардио 3–4 раза в неделю, сокращение сахара "
                     "и трансжиров, увеличение клетчатки (овощи, крупы).",
                severity="warning",
            ))
        elif snap.visceral_fat_level > 10:
            tips.append(Tip(
                icon="warning",
                title="Висцеральный жир повышен",
                body=f"Уровень {snap.visceral_fat_level} (норма — до 10). "
                     "Добавьте регулярные кардиотренировки и "
                     "сократите быстрые углеводы и алкоголь.",
                severity="info",
            ))

    # Процент жира — по нормам InBody.
    # Мужчины: 8–19% норма, женщины: 21–33% норма.
    if snap.sex == "male":
        fat_low, fat_high = 8.0, 19.0
    else:
        fat_low, fat_high = 21.0, 33.0

    if snap.body_fat_percent > fat_high + 5:
        tips.append(Tip(
            icon="monitor_heart",
            title="Процент жира значительно выше нормы",
            body=f"Сейчас {snap.body_fat_percent:.1f}% "
                 f"(норма для {'мужчин' if snap.sex == 'male' else 'женщин'} — "
                 f"{fat_low:.0f}–{fat_high:.0f}%). "
                 "Сочетайте дефицит калорий (300–500 ккал) с силовыми "
                 "тренировками, чтобы сохранить мышцы при похудении.",
            severity="warning",
        ))
    elif snap.body_fat_percent > fat_high:
        tips.append(Tip(
            icon="monitor_heart",
            title="Процент жира немного выше нормы",
            body=f"Сейчас {snap.body_fat_percent:.1f}% "
                 f"(норма — до {fat_high:.0f}%). "
                 "Небольшой дефицит калорий и регулярные тренировки "
                 "помогут вернуться в норму.",
            severity="info",
        ))
    elif snap.body_fat_percent < fat_low:
        tips.append(Tip(
            icon="monitor_heart",
            title="Процент жира ниже нормы",
            body=f"Сейчас {snap.body_fat_percent:.1f}% "
                 f"(норма — от {fat_low:.0f}%). "
                 "Слишком низкий жир может нарушить гормональный баланс. "
                 "Не сокращайте калории дальше.",
            severity="warning",
        ))
