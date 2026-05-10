"""Pure helpers для аналитики InBody — spec 010.

- `select_metric` — единый source-of-truth для имён метрик: маппит string
  → атрибут InBodyMeasurement и нормализует Decimal/None в float/None.
- `compute_deltas` — для compare-эндпоинта: список `FieldDelta` по всем
  сравнимым полям между двумя замерами.
- `forecast_to_dated_points` — преобразование ForecastBundle (горизонты в
  неделях) к абсолютным датам для overlay на графике (spec 010 REQ-03).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Literal

# Метрики, по которым можно построить серию (REQ-01 + REQ-02). Включают
# height_cm, потому что в редких случаях рост может меняться (рост у
# подростков), но в UI обычно скрыт. Сам список — единый for both
# select_metric() и валидации в API.
SeriesMetric = Literal[
    "weight_kg",
    "height_cm",
    "body_fat_percent",
    "muscle_mass_kg",
    "body_water_percent",
    "protein_kg",
    "minerals_kg",
    "visceral_fat_level",
    "bmr_kcal",
    "fat_free_mass_kg",
    "bmi",
]

SERIES_METRICS: tuple[str, ...] = (
    "weight_kg",
    "height_cm",
    "body_fat_percent",
    "muscle_mass_kg",
    "body_water_percent",
    "protein_kg",
    "minerals_kg",
    "visceral_fat_level",
    "bmr_kcal",
    "fat_free_mass_kg",
    "bmi",
)

# Метрики, для которых spec 008 умеет строить прогноз. Прочие в overlay
# на графике вернутся как None — UI не нарисует пунктир.
FORECASTABLE_METRICS: tuple[str, ...] = (
    "weight_kg",
    "body_fat_percent",
    "muscle_mass_kg",
)

# Поля для compare-таблицы. height_cm/sex намеренно опущены: рост-снапшот
# берётся из профиля и редко меняется, sex не сравнивается арифметически.
COMPARABLE_FIELDS: tuple[str, ...] = (
    "weight_kg",
    "body_fat_percent",
    "muscle_mass_kg",
    "body_water_percent",
    "protein_kg",
    "minerals_kg",
    "visceral_fat_level",
    "bmr_kcal",
    "fat_free_mass_kg",
    "bmi",
)


def select_metric(measurement: Any, metric: str) -> float | None:
    """Прочитать значение метрики из measurement.

    Возвращаем `float` (включая для целых полей вроде `bmr_kcal` — для
    серии важна численность, а не int/float-различие). `None` — если поля
    нет (например, partial-замер без muscle_mass_kg).
    """
    if metric not in SERIES_METRICS:
        raise ValueError(f"unknown metric: {metric!r}")
    value = getattr(measurement, metric, None)
    if value is None:
        return None
    return float(value)


@dataclass(frozen=True)
class FieldDelta:
    """Разница одной метрики между двумя замерами.

    `value_a`/`value_b` — оба None если метрики нет ни в одном замере;
    в этом случае delta тоже None. Если значение есть только в одном —
    delta_absolute/percent тоже None: percentage без знаменателя
    бессмысленно показывать.
    """

    field: str
    value_a: float | None
    value_b: float | None
    delta_absolute: float | None
    delta_percent: float | None


def _round(value: float, places: int) -> float:
    return round(value, places)


def compute_deltas(
    a: Any,
    b: Any,
    *,
    fields: tuple[str, ...] = COMPARABLE_FIELDS,
) -> list[FieldDelta]:
    """Список дельт по `fields` между двумя замерами.

    `a` — «было», `b` — «стало», поэтому `delta = b - a`. Положительное
    значение → метрика выросла. UI решает, выросла ли «в лучшую сторону»,
    исходя из цели пользователя (weight_loss vs muscle_gain).
    """
    out: list[FieldDelta] = []
    for fname in fields:
        va_raw = getattr(a, fname, None)
        vb_raw = getattr(b, fname, None)
        va = float(va_raw) if va_raw is not None else None
        vb = float(vb_raw) if vb_raw is not None else None
        if va is None or vb is None:
            out.append(
                FieldDelta(
                    field=fname,
                    value_a=va,
                    value_b=vb,
                    delta_absolute=None,
                    delta_percent=None,
                )
            )
            continue
        abs_delta = vb - va
        pct = (abs_delta / va * 100.0) if va != 0 else None
        out.append(
            FieldDelta(
                field=fname,
                value_a=va,
                value_b=vb,
                delta_absolute=_round(abs_delta, 2),
                delta_percent=_round(pct, 2) if pct is not None else None,
            )
        )
    return out


@dataclass(frozen=True)
class DatedForecastPoint:
    """Точка прогноза на абсолютной дате — для overlay на graphics."""

    date: date
    value: float
    ci_low: float
    ci_high: float


def forecast_to_dated_points(
    *,
    metric: str,
    bundle: Any,
    anchor_date: date,
) -> list[DatedForecastPoint]:
    """Преобразовать ForecastBundle для одной метрики в датированные точки.

    `anchor_date` — дата последнего замера, от которой считаются горизонты
    в неделях (см. `predictor.ForecastPoint.horizon_weeks`).

    Если `metric` не из FORECASTABLE_METRICS — возвращаем пустой список,
    UI не рисует пунктир. Так упрощается вызывающий код: можно дёргать
    `forecast_to_dated_points` для любой метрики, не сверяясь со списком.
    """
    if metric not in FORECASTABLE_METRICS:
        return []
    series = getattr(bundle, metric, None)
    if series is None:
        return []
    out: list[DatedForecastPoint] = []
    for fp in series.points:
        out.append(
            DatedForecastPoint(
                date=anchor_date + timedelta(weeks=int(fp.horizon_weeks)),
                value=float(fp.point),
                ci_low=float(fp.ci_low),
                ci_high=float(fp.ci_high),
            )
        )
    return out
