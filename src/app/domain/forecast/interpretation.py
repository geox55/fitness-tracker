"""Rule-based текстовая интерпретация прогноза (REQ-05).

Пишем коротко: 1-2 предложения, по дельте к 4-недельному горизонту.
Логика разделена по знаку дельты и по основному «двигателю» (вес ↓ ←→
жир ↓ → значит, потеря за счёт жира; вес ↑ + мышцы ↑ → набор сухой массы).
"""

from __future__ import annotations


def _round1(v: float) -> str:
    return f"{abs(v):.1f}"


def build_interpretation(
    *,
    weight_delta_kg: float,
    fat_delta_percent: float,
    muscle_delta_kg: float,
    horizon_weeks: int,
    confidence: str,
    fallback: bool,
) -> str:
    """Короткий текст под графиком прогноза.

    Логика:
    - |delta_weight| < 0.3 кг → «вес стабилизируется»
    - delta_weight < 0 и delta_fat < 0 → потеря за счёт жира
    - delta_weight > 0 и delta_muscle > 0 → набор сухой массы
    - delta_weight < 0 и delta_muscle < 0 → потеря и жира и мышц (предупреждение)
    """
    horizon_text = f"{horizon_weeks} недел"
    if horizon_weeks == 1:
        horizon_text += "ю"
    elif horizon_weeks in (2, 3, 4):
        horizon_text += "и"
    else:
        horizon_text += "ь"

    parts: list[str] = []

    if abs(weight_delta_kg) < 0.3:
        parts.append(f"При текущем темпе вес стабильный за {horizon_text}.")
    elif weight_delta_kg < 0:
        if fat_delta_percent < -0.3:
            parts.append(
                f"При текущем темпе вы потеряете ~{_round1(weight_delta_kg)} кг "
                f"за {horizon_text}, преимущественно за счёт жира."
            )
        elif muscle_delta_kg < -0.2:
            parts.append(
                f"При текущем темпе ожидается потеря {_round1(weight_delta_kg)} кг "
                f"за {horizon_text}, но часть — за счёт мышц. Стоит пересмотреть план."
            )
        else:
            parts.append(
                f"При текущем темпе вы потеряете ~{_round1(weight_delta_kg)} кг "
                f"за {horizon_text}."
            )
    else:  # weight_delta > 0
        if muscle_delta_kg > 0.2:
            parts.append(
                f"При текущем темпе вы наберёте ~{_round1(weight_delta_kg)} кг "
                f"за {horizon_text}, в том числе мышечную массу."
            )
        else:
            parts.append(
                f"При текущем темпе ожидается набор {_round1(weight_delta_kg)} кг "
                f"за {horizon_text}."
            )

    if confidence == "low":
        parts.append("Прогноз станет точнее после ещё 2 InBody-измерений.")
    if fallback:
        parts.append("Использован базовый расчёт по тренду.")

    return " ".join(parts)
