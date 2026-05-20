"""Извлечение полей InBody из текста PDF — REQ-02..05 spec 013.

Подход — labels + regex. На реальных PDF-извлечениях текст бывает шумным
(`ll9. 7lbs.` вместо `119.7 lbs.`, `lnBody520` вместо `InBody520`), поэтому:
- normalize_decimal() терпимо относится к пробелам внутри числа,
- regex'ы с `\\s*` между значащими частями,
- сначала пробуем «model-specific»-pattern (короче — точнее),
  затем generic-fallback (REQ-03).

Никаких сетевых вызовов, никакого I/O. Парсер — pure-функция,
полностью покрытая юнит-тестами на сохранённых фрагментах текста.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

# Маркеры, по которым понимаем «это InBody» (REQ-06, Scenario 4).
# `lnBody` — частая ошибка OCR/extract'а («I» → «l»); ловим оба.
# Русские маркеры — для локализованных PDF из российских клиник; ни
# латинской `InBody`, ни `PBF` там нет, поэтому полагаемся на устойчивые
# заголовки разделов отчёта.
_INBODY_MARKERS: tuple[str, ...] = (
    "InBody",
    "lnBody",
    "Body Composition Analysis",
    "PBF",
    "Skeletal Muscle Mass",
    "ECW/TBW",
    "Body Composition Result Sheet",
    "Состав тела",
    "История состава тела",
    "Висцеральный жир",
    "Безжировая масса",
    "Индекс массы тела",
)

UnitsHint = Literal["metric", "imperial"]
Confidence = Literal["high", "medium", "low"]
Template = Literal["inbody_270", "inbody_570", "inbody_770", "inbody_970", "generic"]

# Все целевые поля, которые мы стараемся вытащить (соответствуют InBody-моделям).
_TARGET_FIELDS: tuple[str, ...] = (
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
    "sex",
)


@dataclass(frozen=True)
class ParsedInBody:
    """Результат парсинга. Сервис проверит, какой статус Job'у выставить."""

    template: Template | None
    units: UnitsHint
    extracted: dict[str, float | int | str]
    confidence: dict[str, Confidence]
    missing_fields: tuple[str, ...]


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------


# OCR-confusable буквы → цифры. Применяется только при normalize_decimal,
# когда мы уже знаем, что строка должна быть числом.
_OCR_TO_DIGIT = str.maketrans({"l": "1", "I": "1", "O": "0", "o": "0"})


def normalize_decimal(raw: str) -> float | None:
    """`'119,7'` → 119.7; `'ll9. 7lbs'` → 119.7; `'1 331'` → 1331.

    Реальные PDF-извлечения часто содержат пробелы внутри числа (артефакт
    layout-парсера) и OCR-путаницу `l`↔`1`, `O`↔`0`. Терпимо чистим
    всё, что не цифра/точка, оставляя один знак минуса спереди если есть.
    """
    if raw is None:
        return None
    s = raw.strip()
    if not s:
        return None
    sign = "-" if s.startswith("-") else ""
    # Сначала приводим OCR-confusable буквы к цифрам (l/I→1, O/o→0).
    s = s.translate(_OCR_TO_DIGIT)
    # Запятая → точка.
    s = s.replace(",", ".")
    # Убрать всё, кроме цифр и точек.
    s = re.sub(r"[^\d.]", "", s)
    if not s or s == ".":
        return None
    # Если несколько точек — оставить первую (артефакт «21. 6lbs.»).
    if s.count(".") > 1:
        head, _, tail = s.partition(".")
        s = f"{head}.{tail.replace('.', '')}"
    try:
        return float(sign + s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Распознавание шаблонов
# ---------------------------------------------------------------------------


_TEMPLATE_PATTERNS: tuple[tuple[Template, re.Pattern[str]], ...] = (
    ("inbody_970", re.compile(r"\b[Il]n[Bb]ody\s*970\b")),
    ("inbody_770", re.compile(r"\b[Il]n[Bb]ody\s*770\b")),
    ("inbody_570", re.compile(r"\b[Il]n[Bb]ody\s*570\b")),
    ("inbody_270", re.compile(r"\b[Il]n[Bb]ody\s*270\b")),
)


def is_inbody(text: str) -> bool:
    """REQ-06: документ должен иметь хоть один маркер InBody."""
    return any(marker in text for marker in _INBODY_MARKERS)


def detect_template(text: str) -> Template | None:
    """Точная модель аппарата по шапке отчёта; иначе `generic`/None.

    None → ни одного маркера InBody (вызывающий сервис вернёт 'not_inbody').
    """
    if not is_inbody(text):
        return None
    for tmpl, pattern in _TEMPLATE_PATTERNS:
        if pattern.search(text):
            return tmpl
    return "generic"


# ---------------------------------------------------------------------------
# Конверсия единиц
# ---------------------------------------------------------------------------


_LB_TO_KG = 0.45359237
_INCH_TO_CM = 2.54


def _detect_units(text: str) -> UnitsHint:
    """Если в тексте чаще встречаются 'lbs'/'in.' — imperial, иначе metric.

    Простая эвристика по числу совпадений ключевых слов. Шаблоны от InBody
    Asia/Europe приходят в metric, US — в imperial.
    """
    imperial_hits = (
        len(re.findall(r"\blbs?\b\.?", text)) +
        len(re.findall(r"\bft\b", text)) +
        len(re.findall(r"\bin\b\.?", text))
    )
    metric_hits = (
        len(re.findall(r"\bkg\b", text)) +
        len(re.findall(r"\bcm\b", text))
    )
    return "imperial" if imperial_hits > metric_hits else "metric"


def _to_kg(value: float, units: UnitsHint) -> float:
    return value * _LB_TO_KG if units == "imperial" else value


def _to_cm_from_height_imperial(text: str) -> float | None:
    """Imperial-рост: `5ft 06.0in`, `5'6\"`, или замусоренный `5ft06. 01 n.`
    (Brown 520 — `1 n.` вместо `in.`).
    """
    patterns = (
        r"(\d{1,2})\s*(?:ft|')\s*(\d{1,2}(?:[.\s]\d+)?)\s*(?:in|\")",
        # OCR-noise: «5ft06. 01 n.» — `1 n` вместо `in`, и дробь имеет
        # пробел внутри. Группа 2 захватывает «06. 0» — нормализуется в 6.0.
        r"(\d{1,2})\s*ft\s*(\d{1,2}\.?\s*\d*)\s*[1lI]\s*n\.?",
    )
    for pat in patterns:
        m = re.search(pat, text)
        if m is None:
            continue
        feet = int(m.group(1))
        inches_raw = m.group(2)
        inches = normalize_decimal(inches_raw)
        if inches is None:
            continue
        return round((feet * 12 + inches) * _INCH_TO_CM, 1)
    return None


# ---------------------------------------------------------------------------
# Поле-за-полем экстракторы
# ---------------------------------------------------------------------------

# Формат: для каждого поля — список regex'ов; первый удачный матч побеждает.
# `(?:\s|\.)` между числом и единицей измерения — толерантно к шуму PDF.
# Группа 1 — само число.

# Терпит OCR-confusable (`l`/`I`/`O`/`o` рядом с цифрами), пробелы и запятые
# внутри. Сама группа всегда содержит хотя бы одну реальную цифру, чтобы
# не ловить «only-letters» куски типа «llo».
_NUMBER = r"((?:[-+]?[\dlIOo .,]*\d[\dlIOo .,]*|\d))"

# Узкий gap: запрещаем не только цифры, но и OCR-confusable `l/I/O/o`,
# потому что они могут быть началом числа (`ll9.7lbs`). Иначе greedy gap
# проглотит буквенные начала числа, и group 1 захватит только «9.7».
_GAP_NARROW = r"[^\dlIOo\n]"
# Широкий gap: разрешаем буквы, нужно для labels со скобками типа
# «BMI (Body Mass Index)» или «PBF (%)».
_GAP_WIDE = r"[^\d\n]"
# Для русских PDF между label и числом часто стоит вердикт («Выше нормы»,
# «Норма», «Ниже нормы»). Берём широкий gap без перевода строк, до ~30 симв.
_GAP_RU = r"[^\d\n]{0,30}"


_FIELD_PATTERNS: dict[str, tuple[str, ...]] = {
    # Вес: основной label — «body weight» (полная фраза в реальном PDF
    # InBody 520) или просто «Weight» в шапке table-format отчётов;
    # после буквенного label-а допустимы только разделители (не цифры),
    # затем число с единицей измерения.
    "weight": (
        # Brown 520: «Your body weight,ll9. 7lbs.» — label «body weight»,
        # запятая, число с lbs (с OCR-`l`).
        r"body\s+weight" + _GAP_NARROW + r"{0,15}" + _NUMBER + r"\s*(?:kg|lbs?|кг)",
        # Generic: одиночная пометка «Weight ... 80.5 kg».
        r"\bWeight\b" + _GAP_NARROW + r"{0,30}" + _NUMBER + r"\s*(?:kg|lbs?|кг)",
        # Русский табличный: «Вес, кг 82,2».
        r"Вес,\s*кг\s*" + _NUMBER,
        # Русский шапочный: «Вес Выше нормы 82.2 кг» / «Вес 82,2 кг».
        r"Вес" + _GAP_RU + _NUMBER + r"\s*кг",
    ),
    "body_fat_percent": (
        # «Percentage of Body Fat ... 18.1» — `_GAP_WIDE`, потому что
        # между Body Fat и числом могут быть буквенные пояснения.
        r"(?:Percent(?:age)?\s+of\s+Body\s+Fat|PBF)" + _GAP_WIDE + r"{0,40}"
        + _NUMBER + r"\s*(?:%|percent)?",
        # «PBF (%) 18.1» — табличный формат, label-в-скобках.
        r"PBF\s*\(\s*%\s*\)\s*" + _NUMBER + r"\b",
        # Русский табличный: «Жир, % 29,1».
        r"Жир,\s*%\s*" + _NUMBER,
        # Русский шапочный: «Жир Выше нормы 29.1 %».
        r"Жир" + _GAP_RU + _NUMBER + r"\s*%",
    ),
    "muscle_mass": (
        r"(?:Skeletal\s+Muscle\s+Mass|SMM|Muscle\s+Mass|Мышечная\s+масса)"
        + _GAP_NARROW + r"{0,40}" + _NUMBER + r"\s*(?:kg|lbs?|кг)",
        # Русский табличный: «Мышцы, кг 32,8».
        r"Мышцы,\s*кг\s*" + _NUMBER,
        # Русский шапочный: «Мышцы Норма 32.8 кг» / «Мышцы 32.8 кг».
        r"Мышцы" + _GAP_RU + _NUMBER + r"\s*кг",
    ),
    "body_water_percent": (
        r"(?:Total\s+Body\s+Water|TBW)" + _GAP_NARROW + r"{0,40}" + _NUMBER + r"\s*%",
    ),
    "protein": (
        r"Protein" + _GAP_NARROW + r"{0,30}" + _NUMBER + r"\s*(?:kg|lbs?)",
        # Русский: «Белок 11.6 кг».
        r"Белок" + _GAP_RU + _NUMBER + r"\s*кг",
    ),
    "minerals": (
        r"(?:Minerals?|non-osseous\s+Minerals)" + _GAP_NARROW + r"{0,30}"
        + _NUMBER + r"\s*(?:kg|lbs?)",
        # Русский: «Кости Выше нормы 4.09 кг».
        r"Кости" + _GAP_RU + _NUMBER + r"\s*кг",
    ),
    "visceral_fat_level": (
        r"Visceral\s+Fat(?:\s+Level)?" + _GAP_NARROW + r"{0,30}" + _NUMBER + r"\b",
        # Русский: «Висцеральный жир 9».
        r"Висцеральный\s+жир" + r"[^\d\n]{0,10}" + _NUMBER,
    ),
    "bmr_kcal": (
        # Самый сильный индикатор — число прямо перед «kcal». В отчёте
        # InBody это всегда BMR. Первое совпадение обычно и есть BMR.
        r"\b" + _NUMBER + r"\s*kcal\b",
        r"BMR\s*\(?kcal\)?\s*" + _NUMBER + r"\b",
        # Русский: «Обмен веществ 1628». ВАЖНО: «Суточная норма калорий»
        # (TDEE) — это другое поле; для BMR берём только «Обмен веществ».
        r"Обмен\s+веществ" + r"[^\d\n]{0,20}" + _NUMBER,
    ),
    "fat_free_mass": (
        r"(?:Fat\s+Free\s+Mass|FFM|Lean\s+Body\s+Mass)"
        + _GAP_NARROW + r"{0,40}" + _NUMBER + r"\s*(?:kg|lbs?)",
        # Русский: «Безжировая масса 58.2 кг».
        r"Безжировая\s+масса" + _GAP_RU + _NUMBER + r"\s*кг",
    ),
    "bmi": (
        # «BMI 19.3» / «BMI (Body Mass Index) 26.3». Используем `_GAP_WIDE`,
        # потому что между BMI и числом часто буквенные пояснения в скобках.
        # Lookahead `(?!\s*[/=])` отсеивает формулу
        # «BMI = Weight,kg / (Height,m)²».
        r"BMI" + _GAP_WIDE + r"{0,60}" + _NUMBER + r"(?!\s*[/=])\b",
        # Русский: «Индекс массы тела Выше нормы 28.4».
        r"Индекс\s+массы\s+тела" + _GAP_RU + _NUMBER,
    ),
    "height": (
        # Metric: «Height 175 cm»
        r"Height" + _GAP_NARROW + r"{0,20}" + _NUMBER + r"\s*cm",
        # Русский: «Рост 170 см».
        r"Рост" + r"[^\d\n]{0,10}" + _NUMBER + r"\s*см",
    ),
}


def _first_match(
    text: str, patterns: tuple[str, ...], *, dotall: bool = False
) -> float | None:
    flags = re.IGNORECASE | (re.DOTALL if dotall else 0)
    for pat in patterns:
        m = re.search(pat, text, flags=flags)
        if m is None:
            continue
        value = normalize_decimal(m.group(1))
        if value is not None:
            return value
    return None


def _extract_sex(text: str) -> str | None:
    m = re.search(r"\bGender\s*[:.]?\s*(Male|Female|M|F)\b", text, re.IGNORECASE)
    if m is not None:
        raw = m.group(1).lower()
        if raw in ("male", "m"):
            return "male"
        if raw in ("female", "f"):
            return "female"
    # Русский: «Пол М» / «Пол Ж» в шапке отчёта.
    m_ru = re.search(r"Пол\s+([МЖ])(?:\s|$)", text)
    if m_ru is not None:
        return "male" if m_ru.group(1) == "М" else "female"
    return None


# ---------------------------------------------------------------------------
# Главный extract
# ---------------------------------------------------------------------------


@dataclass
class _Extraction:
    extracted: dict[str, float | int | str] = field(default_factory=dict)
    confidence: dict[str, Confidence] = field(default_factory=dict)


def _add(
    out: _Extraction, key: str, value: float | int | str | None, conf: Confidence
) -> None:
    if value is None:
        return
    out.extracted[key] = value
    out.confidence[key] = conf


def extract_fields(text: str) -> ParsedInBody:
    """Главный entry point парсера.

    Возвращает значения в **метрической** системе (kg/cm) — даже если PDF
    был в imperial: внутри сразу конвертируем. Это упрощает дальнейший
    flow: сервис сохраняет в БД ровно то, что вернул парсер, без
    дополнительных преобразований.
    """
    template = detect_template(text)
    units = _detect_units(text)
    out = _Extraction()

    # Confidence: high — поле найдено по template-specific pattern;
    # medium — generic; low — fallback (сейчас medium=generic, high=template).
    base_conf: Confidence = "high" if template not in (None, "generic") else "medium"

    # weight
    w = _first_match(text, _FIELD_PATTERNS["weight"])
    if w is not None:
        _add(out, "weight_kg", round(_to_kg(w, units), 2), base_conf)

    # height
    h_metric = _first_match(text, _FIELD_PATTERNS["height"])
    if h_metric is not None:
        _add(out, "height_cm", round(h_metric, 1), base_conf)
    elif units == "imperial":
        h_imp = _to_cm_from_height_imperial(text)
        if h_imp is not None:
            _add(out, "height_cm", h_imp, base_conf)

    # body_fat_percent
    fat = _first_match(text, _FIELD_PATTERNS["body_fat_percent"])
    if fat is not None:
        _add(out, "body_fat_percent", round(fat, 1), base_conf)

    # muscle_mass
    mm = _first_match(text, _FIELD_PATTERNS["muscle_mass"])
    if mm is not None:
        _add(out, "muscle_mass_kg", round(_to_kg(mm, units), 2), base_conf)

    # body_water_percent
    water = _first_match(text, _FIELD_PATTERNS["body_water_percent"])
    if water is not None:
        _add(out, "body_water_percent", round(water, 1), base_conf)

    # protein
    protein = _first_match(text, _FIELD_PATTERNS["protein"])
    if protein is not None:
        _add(out, "protein_kg", round(_to_kg(protein, units), 2), base_conf)

    # minerals
    minerals = _first_match(text, _FIELD_PATTERNS["minerals"])
    if minerals is not None:
        _add(out, "minerals_kg", round(_to_kg(minerals, units), 2), base_conf)

    # visceral fat level (целое число)
    vfl = _first_match(text, _FIELD_PATTERNS["visceral_fat_level"])
    if vfl is not None:
        _add(out, "visceral_fat_level", round(vfl), base_conf)

    # BMR — разрешаем переносы строк между label и значением.
    bmr = _first_match(text, _FIELD_PATTERNS["bmr_kcal"], dotall=True)
    if bmr is not None and 500 <= bmr <= 5000:
        _add(out, "bmr_kcal", round(bmr), base_conf)

    # fat_free_mass
    ffm = _first_match(text, _FIELD_PATTERNS["fat_free_mass"])
    if ffm is not None:
        _add(out, "fat_free_mass_kg", round(_to_kg(ffm, units), 2), base_conf)

    # BMI — может встречаться вместе с label-инструкцией («BMI = Weight,kg / Height,m²»);
    # в этом случае нужный вариант — без `=`.
    bmi = _first_match(text, _FIELD_PATTERNS["bmi"])
    if bmi is not None and 5 < bmi < 80:
        _add(out, "bmi", round(bmi, 1), base_conf)

    # sex
    sex = _extract_sex(text)
    if sex is not None:
        _add(out, "sex", sex, base_conf)

    missing = tuple(f for f in _TARGET_FIELDS if f not in out.extracted)
    return ParsedInBody(
        template=template,
        units=units,
        extracted=out.extracted,
        confidence=out.confidence,
        missing_fields=missing,
    )
