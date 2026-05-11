"""Сборка PDF-отчёта — pure helper для spec 010 §3 Scenario 5 / REQ-10..12.

На вход — typed `ReportData` (что собрал сервис из БД), на выход — bytes
готового PDF. Никаких I/O, БД и сетевых вызовов; легко тестируется.

Дизайн-решения:

- **Язык PDF — английский.** Reportlab из коробки даёт Helvetica/Times,
  которые не поддерживают кириллицу; чтобы не тащить в репо TTF (~700 KB)
  и не зависеть от системных шрифтов, отчёт собирается на латинице.
  UI рядом с кнопкой «Экспорт PDF» предупреждает пользователя.
- **Reportlab Platypus** (Story / SimpleDocTemplate): декларативное API,
  автоматический pagination, поддержка таблиц и keep-together; лучше для
  отчётов, чем низкоуровневый Canvas.
- **Пустая секция = нет секции.** Если в `ReportData` для секции пришли
  пустые данные, в PDF её не печатаем — иначе у пользователя без InBody
  отчёт будет состоять из подписи и заголовков пустых разделов.
- **Page limit = 50** (spec 010 Edge Cases). Достигается через тримминг
  inbody-серий до первой/последней даты (downsampling), не через жёсткий
  обрез страниц — иначе таблица оборвётся посередине строки.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Лимит на количество строк в InBody-таблице: 5 точек на сантиметр × ~25 см
# полезной высоты × ~5 страниц/секция = ~625. Берём с запасом 500, чтобы
# уложиться в общий лимит 50 страниц при максимальной заполненности
# (4 секции × ~12 страниц + шапка ≈ 50). Превышение → downsample.
INBODY_MAX_ROWS = 500
WORKOUTS_MAX_ROWS = 200
MAX_PAGES = 50


@dataclass(frozen=True)
class ProfileSection:
    """Шапка отчёта о пользователе. Все поля опциональны, кроме display_name.

    `email` сюда намеренно не попадает — REQ-11 говорит «без PII вне выбора
    пользователя», а явного opt-in для email мы пока не вводим.
    """

    display_name: str
    sex: str | None
    age: int | None
    height_cm: float | None
    goal: str | None
    target_weight_kg: float | None
    target_muscle_kg: float | None


@dataclass(frozen=True)
class InBodySeriesSection:
    """Три ключевые метрики (REQ-11). Каждая — (date, value) точки."""

    weight: list[tuple[date, float]]
    body_fat_percent: list[tuple[date, float]]
    muscle_mass_kg: list[tuple[date, float]]

    def is_empty(self) -> bool:
        return not self.weight and not self.body_fat_percent and not self.muscle_mass_kg


@dataclass(frozen=True)
class WorkoutsSection:
    """Тоннаж + кол-во тренировок по периодам (REQ-07/08)."""

    bucket: str  # day | week | month
    items: list[tuple[date, float, int]]  # (period_start, tonnage_kg, workouts)

    def is_empty(self) -> bool:
        return not self.items


@dataclass(frozen=True)
class GoalProgressSection:
    """Текущий прогресс по цели + опц. ETA из прогноза (REQ-05/06)."""

    goal: str  # weight_loss | muscle_gain
    start_value: float
    current_value: float
    target_value: float
    progress_percent: int
    eta: date | None


@dataclass(frozen=True)
class ReportData:
    generated_at: date
    period_from: date | None
    period_to: date | None
    profile: ProfileSection | None
    inbody: InBodySeriesSection | None
    workouts: WorkoutsSection | None
    goal: GoalProgressSection | None


# ---------------------------------------------------------------------------
# Helpers сборки секций (each returns a list of Flowables)
# ---------------------------------------------------------------------------


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "Title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=18, spaceAfter=12,
        ),
        "H2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, spaceBefore=10, spaceAfter=6,
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, spaceAfter=4,
        ),
        "Small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8, textColor=colors.grey,
        ),
    }


def _table(headers: list[str], rows: list[list[str]]) -> Table:
    """Стилизованная таблица: жирная шапка + zebra-фон строк, тонкие линии."""
    data = [headers, *rows]
    tbl = Table(data, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F8F8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl


def _downsample(rows: list[tuple[date, float]], cap: int) -> list[tuple[date, float]]:
    """Если строк больше cap, берём равномерную выборку из cap элементов.

    Сохраняем первую и последнюю точки — UI/читателю важны границы окна.
    Промежуточные индексы линейно. Это «визуальный» downsample, не
    статистически взвешенный — для отчёта достаточно.
    """
    if len(rows) <= cap:
        return rows
    step = (len(rows) - 1) / (cap - 1)
    return [rows[round(i * step)] for i in range(cap)]


def _header(data: ReportData, styles: dict[str, ParagraphStyle]) -> list[object]:
    parts: list[object] = [
        Paragraph("Fitness Tracker — Progress Report", styles["Title"]),
    ]
    period = "all time"
    if data.period_from is not None and data.period_to is not None:
        period = f"{data.period_from.isoformat()} — {data.period_to.isoformat()}"
    elif data.period_from is not None:
        period = f"from {data.period_from.isoformat()}"
    elif data.period_to is not None:
        period = f"until {data.period_to.isoformat()}"
    parts.append(Paragraph(
        f"Generated on {data.generated_at.isoformat()} · Period: {period}",
        styles["Small"],
    ))
    parts.append(Spacer(1, 0.4 * cm))
    return parts


def _profile_block(
    section: ProfileSection, styles: dict[str, ParagraphStyle]
) -> list[object]:
    rows: list[list[str]] = [["Name", section.display_name]]
    if section.sex is not None:
        rows.append(["Sex", section.sex])
    if section.age is not None:
        rows.append(["Age", str(section.age)])
    if section.height_cm is not None:
        rows.append(["Height", f"{section.height_cm:g} cm"])
    if section.goal is not None:
        rows.append(["Goal", section.goal])
    if section.target_weight_kg is not None:
        rows.append(["Target weight", f"{section.target_weight_kg:g} kg"])
    if section.target_muscle_kg is not None:
        rows.append(["Target muscle", f"{section.target_muscle_kg:g} kg"])
    return [
        Paragraph("Profile", styles["H2"]),
        _table(["Field", "Value"], rows),
        Spacer(1, 0.3 * cm),
    ]


def _inbody_block(
    section: InBodySeriesSection, styles: dict[str, ParagraphStyle]
) -> list[object]:
    """Одна таблица: дата + три метрики; пустые ячейки оставляем «—»."""
    # Объединяем индекс дат по всем трём метрикам, чтобы было одно общее
    # измерение на строку (даже если в этот день не во всех метриках есть
    # значение).
    by_date: dict[date, dict[str, float]] = {}
    for d, v in section.weight:
        by_date.setdefault(d, {})["weight"] = v
    for d, v in section.body_fat_percent:
        by_date.setdefault(d, {})["fat"] = v
    for d, v in section.muscle_mass_kg:
        by_date.setdefault(d, {})["muscle"] = v
    sorted_dates = sorted(by_date)
    # Downsample, если измерений слишком много (см. doc у INBODY_MAX_ROWS).
    indexed = _downsample(
        [(d, 0.0) for d in sorted_dates], INBODY_MAX_ROWS
    )
    kept = [d for d, _ in indexed]

    rows: list[list[str]] = []
    for d in kept:
        cells = by_date[d]
        rows.append([
            d.isoformat(),
            f"{cells['weight']:g}" if "weight" in cells else "—",
            f"{cells['fat']:g}" if "fat" in cells else "—",
            f"{cells['muscle']:g}" if "muscle" in cells else "—",
        ])
    return [
        Paragraph("InBody Measurements", styles["H2"]),
        _table(
            ["Date", "Weight (kg)", "Body Fat (%)", "Muscle Mass (kg)"],
            rows,
        ),
        Spacer(1, 0.3 * cm),
    ]


def _workouts_block(
    section: WorkoutsSection, styles: dict[str, ParagraphStyle]
) -> list[object]:
    # workouts тоже downsample на всякий случай — большие истории по дням
    # могут давать сотни строк.
    sorted_items = sorted(section.items, key=lambda x: x[0])
    # _downsample работает с (date, float); тут нужен (date, float, int) — пишем in-place
    if len(sorted_items) > WORKOUTS_MAX_ROWS:
        step = (len(sorted_items) - 1) / (WORKOUTS_MAX_ROWS - 1)
        sorted_items = [
            sorted_items[round(i * step)] for i in range(WORKOUTS_MAX_ROWS)
        ]
    rows = [
        [it[0].isoformat(), f"{it[1]:g}", str(it[2])]
        for it in sorted_items
    ]
    return [
        Paragraph(
            f"Workouts (per {section.bucket})", styles["H2"]
        ),
        _table(
            ["Period start", "Tonnage (kg)", "Workouts"],
            rows,
        ),
        Spacer(1, 0.3 * cm),
    ]


def _goal_block(
    section: GoalProgressSection, styles: dict[str, ParagraphStyle]
) -> list[object]:
    eta = section.eta.isoformat() if section.eta is not None else "n/a"
    rows = [
        ["Goal", section.goal],
        ["Start", f"{section.start_value:g}"],
        ["Current", f"{section.current_value:g}"],
        ["Target", f"{section.target_value:g}"],
        ["Progress", f"{section.progress_percent}%"],
        ["ETA", eta],
    ]
    return [
        Paragraph("Goal Progress", styles["H2"]),
        _table(["Field", "Value"], rows),
        Spacer(1, 0.3 * cm),
    ]


# ---------------------------------------------------------------------------
# Публичный API
# ---------------------------------------------------------------------------


def build_pdf(data: ReportData) -> bytes:
    """Собрать PDF-отчёт по `data` и вернуть bytes.

    Пустые секции (None или is_empty) не печатаются. Заголовок отчёта и
    сводка периода — всегда. Если ни одной секции с данными — печатаем
    плейсхолдер «No data yet», чтобы PDF не был просто шапкой.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        title="Fitness Tracker Report",
    )
    styles = _styles()
    story: list[object] = []
    story.extend(_header(data, styles))

    rendered_any = False
    if data.profile is not None:
        story.extend(_profile_block(data.profile, styles))
        rendered_any = True
    if data.inbody is not None and not data.inbody.is_empty():
        story.extend(_inbody_block(data.inbody, styles))
        rendered_any = True
    if data.workouts is not None and not data.workouts.is_empty():
        story.extend(_workouts_block(data.workouts, styles))
        rendered_any = True
    if data.goal is not None:
        story.extend(_goal_block(data.goal, styles))
        rendered_any = True

    if not rendered_any:
        story.append(Paragraph("No data yet for the selected period.", styles["Body"]))

    # PageBreak в конце — чтобы reportlab сохранил последнюю страницу;
    # без этого в редких случаях усечётся хвост таблицы.
    story.append(PageBreak())

    doc.build(story)
    return buffer.getvalue()


__all__ = [
    "MAX_PAGES",
    "GoalProgressSection",
    "InBodySeriesSection",
    "ProfileSection",
    "ReportData",
    "WorkoutsSection",
    "build_pdf",
]
