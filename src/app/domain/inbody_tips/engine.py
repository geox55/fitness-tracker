"""Рекомендации на основе ML-прогноза и данных InBody.

ML-модель предсказывает динамику веса, жира и мышц. Этот модуль
интерпретирует прогноз в конкретные действия — продукты, тренировки,
привычки. Нормы взяты из официальной документации InBody и
рекомендаций Роспотребнадзора / ВОЗ.
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
                title="Прогноз: вес растёт",
                body=f"По данным модели вес увеличится на {delta_w:+.1f} кг "
                     f"за {horizon} нед. Для снижения веса создайте умеренный "
                     "дефицит калорий — сократите рацион на 200–300 ккал, "
                     "уменьшите порции быстрых углеводов (сахар, белый хлеб, "
                     "выпечка) и добавьте одну кардиотренировку в неделю. "
                     "Важно сохранить белок в рационе — не менее 1,5 г на кг веса.",
                severity="warning",
            ))
        elif goal == "weight_loss" and delta_w < -0.3:
            tips.append(Tip(
                icon="trending_down",
                title="Вес снижается — хорошая динамика",
                body=f"Модель прогнозирует {delta_w:+.1f} кг за {horizon} нед. "
                     "Вы движетесь к цели. Главное — не снижать калории "
                     "слишком резко: при дефиците более 500 ккал организм "
                     "начинает терять мышечную массу вместе с жиром. "
                     "Ешьте достаточно белка и продолжайте силовые тренировки.",
                severity="success",
            ))
        elif goal == "muscle_gain" and delta_w < -0.2:
            tips.append(Tip(
                icon="trending_down",
                title="Прогноз: вес снижается",
                body=f"Модель показывает {delta_w:+.1f} кг за {horizon} нед. "
                     "Для набора мышечной массы необходим профицит калорий — "
                     "ешьте на 400–500 ккал больше суточной нормы. Добавьте "
                     "сложные углеводы: гречку, бурый рис, овсянку, макароны "
                     "из твёрдых сортов пшеницы. Белок — 1,6–2,2 г на кг веса.",
                severity="warning",
            ))
        elif goal == "muscle_gain" and delta_w > 0.3:
            tips.append(Tip(
                icon="trending_up",
                title="Масса растёт — вы на верном пути",
                body=f"Прогноз: {delta_w:+.1f} кг за {horizon} нед. "
                     "Следите, чтобы рост шёл за счёт мышц, а не жира. "
                     "Оптимальный темп набора — 0,5–1 кг в неделю. Если "
                     "процент жира тоже растёт, немного сократите углеводы.",
                severity="success",
            ))

    if pred_fat is not None:
        delta_f = pred_fat - snap.body_fat_percent
        if delta_f > 0.5:
            tips.append(Tip(
                icon="monitor_heart",
                title="Прогноз: процент жира растёт",
                body=f"Модель предсказывает рост на {delta_f:+.1f}% "
                     f"за {horizon} нед. Сочетайте умеренный дефицит калорий "
                     "с силовыми тренировками — это поможет снизить жировую "
                     "массу и сохранить мышцы. Добавьте 2–3 кардиотренировки "
                     "в неделю (бег, велосипед, плавание) по 30–40 минут.",
                severity="warning",
            ))
        elif delta_f < -0.3:
            tips.append(Tip(
                icon="monitor_heart",
                title="Жировая масса снижается",
                body=f"Прогноз: {delta_f:+.1f}% за {horizon} нед. "
                     "Отличный результат — ваш режим тренировок и питания "
                     "работает. Продолжайте в том же темпе и не забывайте "
                     "про достаточный сон — он важен для восстановления.",
                severity="success",
            ))

    if pred_muscle is not None and snap.muscle_mass_kg is not None:
        delta_m = pred_muscle - snap.muscle_mass_kg
        if goal == "muscle_gain" and delta_m < 0.1:
            tips.append(Tip(
                icon="fitness_center",
                title="Мышечная масса растёт медленно",
                body=f"Прогноз: {delta_m:+.1f} кг за {horizon} нед. "
                     "Для ускорения роста мышц увеличьте потребление белка "
                     "до 2 г на кг веса в день. Лучшие источники: куриная "
                     "грудка, рыба, яйца, творог, бобовые. Добавьте "
                     "прогрессию нагрузки — постепенно увеличивайте рабочие "
                     "веса или количество повторений на каждой тренировке.",
                severity="warning",
            ))
        elif delta_m > 0.2:
            tips.append(Tip(
                icon="fitness_center",
                title="Мышечная масса растёт",
                body=f"Прогноз: {delta_m:+.1f} кг за {horizon} нед. "
                     "Хороший результат. Продолжайте силовые тренировки "
                     "и следите за достаточным потреблением белка и "
                     "качественным сном (7–9 часов) — мышцы растут "
                     "именно во время восстановления.",
                severity="success",
            ))
        elif delta_m < -0.2:
            tips.append(Tip(
                icon="fitness_center",
                title="Прогноз: мышечная масса снижается",
                body=f"Модель показывает {delta_m:+.1f} кг за {horizon} нед. "
                     "Потеря мышц может быть связана с недостатком белка "
                     "или слишком большим дефицитом калорий. Не опускайте "
                     "белок ниже 1,6 г на кг веса, сохраняйте силовые "
                     "тренировки даже на дефиците и высыпайтесь.",
                severity="warning",
            ))


def _tips_from_current(
    snap: MeasurementSnapshot,
    goal: str | None,
    tips: list[Tip],
) -> None:
    # Вода: норма InBody 45–65%. Мышечная ткань на 70–75% состоит из воды,
    # поэтому низкий показатель часто связан с обезвоживанием.
    if snap.body_water_percent is not None:
        if snap.body_water_percent < 45.0:
            tips.append(Tip(
                icon="water_drop",
                title="Низкий уровень воды в организме",
                body=f"Сейчас {snap.body_water_percent:.1f}%, норма — 45–65%. "
                     "Обезвоживание замедляет обмен веществ и снижает "
                     "работоспособность на тренировках. Пейте не менее "
                     "30 мл воды на 1 кг веса в день (для вас — "
                     f"около {snap.weight_kg * 0.03:.1f} л). Ограничьте кофе "
                     "и алкоголь — они выводят жидкость из организма.",
                severity="warning",
            ))
        elif snap.body_water_percent < 50.0:
            tips.append(Tip(
                icon="water_drop",
                title="Уровень воды ниже оптимального",
                body=f"Сейчас {snap.body_water_percent:.1f}%, желательно — от 50%. "
                     "Добавьте 2–3 стакана воды в день, особенно до и после "
                     "тренировки. Ешьте больше овощей и фруктов — огурцы, "
                     "арбуз, помидоры содержат много воды.",
                severity="info",
            ))

    # Белок: норма InBody ~16% от массы тела. Белок — строительный
    # материал для мышц и иммунной системы.
    if snap.protein_kg is not None:
        ratio = snap.protein_kg / snap.weight_kg * 100
        if ratio < 14.0:
            tips.append(Tip(
                icon="egg",
                title="Содержание белка ниже нормы",
                body=f"Белок {snap.protein_kg:.1f} кг ({ratio:.1f}% от веса, "
                     "норма — от 16%). Недостаток белка замедляет "
                     "восстановление мышц и ослабляет иммунитет. "
                     "Включите в каждый приём пищи источник белка: "
                     "куриную грудку, рыбу, яйца, творог или бобовые. "
                     "Перекусывайте орехами или греческим йогуртом.",
                severity="warning",
            ))
        elif ratio < 16.0:
            tips.append(Tip(
                icon="egg",
                title="Белок на нижней границе нормы",
                body=f"Белок {snap.protein_kg:.1f} кг ({ratio:.1f}% от веса, "
                     "норма — 16%). Для поддержания мышечной массы "
                     "добавьте белковый перекус: протеиновый коктейль "
                     "после тренировки, горсть орехов или порцию творога.",
                severity="info",
            ))

    # Минералы: норма InBody 4–6% от массы тела. Это преимущественно
    # кальций и фосфор в костной ткани.
    if snap.minerals_kg is not None:
        ratio = snap.minerals_kg / snap.weight_kg * 100
        if ratio < 4.0:
            tips.append(Tip(
                icon="science",
                title="Содержание минералов ниже нормы",
                body=f"Минералы {snap.minerals_kg:.1f} кг ({ratio:.1f}% от веса, "
                     "норма — 4–6%). Низкий уровень минералов говорит "
                     "о недостатке кальция и фосфора в костях. Добавьте "
                     "в рацион молочные продукты (творог, сыр, кефир), "
                     "кунжут, сардины и листовую зелень (шпинат, брокколи). "
                     "Витамин D помогает усвоению кальция — гуляйте "
                     "на солнце или принимайте добавку (по согласованию с врачом).",
                severity="warning",
            ))
        elif ratio < 5.0:
            tips.append(Tip(
                icon="science",
                title="Минералы на нижней границе нормы",
                body=f"Минералы {snap.minerals_kg:.1f} кг ({ratio:.1f}% от веса, "
                     "норма — 4–6%). Ешьте больше продуктов, богатых кальцием "
                     "и магнием: твёрдый сыр, миндаль, кунжут, сардины, "
                     "листовая зелень. Магний помогает усвоению кальция — "
                     "его много в гречке, бананах и тёмном шоколаде.",
                severity="info",
            ))

    # Висцеральный жир: InBody рекомендует уровень до 10.
    # Это жир вокруг внутренних органов, повышающий риск заболеваний.
    if snap.visceral_fat_level is not None:
        if snap.visceral_fat_level > 15:
            tips.append(Tip(
                icon="warning",
                title="Висцеральный жир значительно повышен",
                body=f"Уровень {snap.visceral_fat_level} (рекомендуемая норма — до 10). "
                     "Висцеральный жир окружает внутренние органы и повышает "
                     "риск диабета и сердечно-сосудистых заболеваний. "
                     "Добавьте кардиотренировки 3–4 раза в неделю по 30–40 мин, "
                     "сократите сахар, трансжиры и алкоголь, увеличьте "
                     "потребление клетчатки (овощи, цельнозерновые крупы).",
                severity="warning",
            ))
        elif snap.visceral_fat_level > 10:
            tips.append(Tip(
                icon="warning",
                title="Висцеральный жир немного повышен",
                body=f"Уровень {snap.visceral_fat_level} (норма — до 10). "
                     "Регулярные кардиотренировки (бег, плавание, велосипед) "
                     "и сокращение быстрых углеводов помогут снизить "
                     "висцеральный жир. Ешьте больше овощей и клетчатки.",
                severity="info",
            ))

    # Процент жира — нормы InBody: мужчины 10–20%, женщины 18–28%.
    if snap.sex == "male":
        fat_low, fat_high = 10.0, 20.0
    else:
        fat_low, fat_high = 18.0, 28.0

    if snap.body_fat_percent > fat_high + 5:
        tips.append(Tip(
            icon="monitor_heart",
            title="Процент жира выше нормы",
            body=f"Сейчас {snap.body_fat_percent:.1f}% "
                 f"(норма для {'мужчин' if snap.sex == 'male' else 'женщин'} — "
                 f"{fat_low:.0f}–{fat_high:.0f}%). "
                 "Для снижения жировой массы сочетайте умеренный дефицит "
                 "калорий (300–500 ккал) с силовыми тренировками — это "
                 "поможет сжигать жир и сохранять мышцы. Сократите "
                 "быстрые углеводы и добавьте больше белка и овощей.",
            severity="warning",
        ))
    elif snap.body_fat_percent > fat_high:
        tips.append(Tip(
            icon="monitor_heart",
            title="Процент жира немного выше нормы",
            body=f"Сейчас {snap.body_fat_percent:.1f}% "
                 f"(норма — до {fat_high:.0f}%). "
                 "Небольшой дефицит калорий и регулярные тренировки "
                 "помогут вернуться в оптимальный диапазон. Не забывайте "
                 "про белок — он важен для сохранения мышечной массы.",
            severity="info",
        ))
    elif snap.body_fat_percent < fat_low:
        tips.append(Tip(
            icon="monitor_heart",
            title="Процент жира ниже нормы",
            body=f"Сейчас {snap.body_fat_percent:.1f}% "
                 f"(норма — от {fat_low:.0f}%). "
                 "Слишком низкий уровень жира может нарушить гормональный "
                 "баланс и ослабить иммунитет. Не сокращайте калории "
                 "дальше и следите за самочувствием.",
            severity="warning",
        ))
