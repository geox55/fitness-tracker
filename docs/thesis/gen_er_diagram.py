"""Генерация ER-диаграммы подсистемы Маши (InBody-прогноз + адаптация плана).

Источник истины — `docs/architecture/02-data-model.md` (там же mermaid-схема).
Здесь отрисовываем фокусную диаграмму: только таблицы, относящиеся к
прогнозу состава тела и адаптации плана, с ключевыми полями и связями.

Результат: docs/thesis/er-diagram-maria.png — встраивается в диплом (раздел
2.8 «Схема базы данных») и может пойти на слайд.

Запуск:  python3 docs/thesis/gen_er_diagram.py
"""

from __future__ import annotations

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ГОСТ: единый шрифт с засечками — как в тексте слайдов/диплома.
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]
plt.rcParams["axes.unicode_minus"] = False

from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent

# ЧБ-оформление (только чёрный/белый, без серого). Группы различаем стилем
# шапки: (заливка, цвет текста, штриховка).
C_FK = "#000000"        # FK-поля — чёрные (как и весь текст)
C_BODY = "#FFFFFF"
C_EDGE = "#000000"
C_LINE = "#000000"
# Группы таблиц
GRP_AUTH = ("#FFFFFF", "#000000", None)       # auth / профиль / замеры
GRP_FORECAST = ("#000000", "#FFFFFF", None)   # ядро прогноза — акцент (чёрная)
GRP_ADAPT = ("#FFFFFF", "#000000", "////")    # адаптация — штриховка

# Каждая сущность: имя, цвет шапки, список полей (PK/FK помечаются),
# левый-нижний угол (x, y) в данных координатах.
FIELD_H = 0.32          # высота строки поля
HEADER_H = 0.42         # высота шапки
BOX_W = 3.0


def _entity(ax, name, fields, x, y, header_style):
    hdr_fc, hdr_tc, hdr_hatch = header_style
    n = len(fields)
    total_h = HEADER_H + n * FIELD_H
    # Тело
    body = FancyBboxPatch(
        (x, y), BOX_W, total_h, boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor=C_BODY, edgecolor=C_EDGE, linewidth=1.3, zorder=2,
    )
    ax.add_patch(body)
    # Шапка
    header = FancyBboxPatch(
        (x, y + total_h - HEADER_H), BOX_W, HEADER_H,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor=hdr_fc, edgecolor=C_EDGE, linewidth=1.3, zorder=3,
        hatch=hdr_hatch,
    )
    ax.add_patch(header)
    # Имя таблицы — на белой подложке, чтобы читалось поверх штриховки.
    ax.text(x + BOX_W / 2, y + total_h - HEADER_H / 2, name,
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=hdr_tc, zorder=4, family="monospace",
            bbox=(dict(boxstyle="round,pad=0.12", fc="white", ec="none")
                  if hdr_hatch else None))
    # Поля
    for i, (label, kind) in enumerate(fields):
        fy = y + total_h - HEADER_H - (i + 0.5) * FIELD_H
        prefix = ""
        weight = "normal"
        color = "#000000"
        if kind == "pk":
            prefix = "PK  "
            weight = "bold"
        elif kind == "fk":
            prefix = "FK  "
            color = C_FK
        ax.text(x + 0.18, fy, prefix + label, ha="left", va="center",
                fontsize=8.5, color=color, fontweight=weight, zorder=4,
                family="monospace")
    return {"x": x, "y": y, "w": BOX_W, "h": total_h,
            "cx": x + BOX_W / 2, "cy": y + total_h / 2}


def _rel(ax, a, b, *, one_a, one_b, label="", side_a="auto", side_b="auto"):
    """Линия связи между сущностями a,b с подписями кардинальности.

    one_a/one_b: '1' или '∞' — что стоит у каждого конца.
    """
    # точки выхода — по ближайшим граням
    ax_, ay = a["cx"], a["cy"]
    bx, by = b["cx"], b["cy"]

    def edge(box, tx, ty):
        # точка на границе box в сторону (tx,ty)
        cx, cy = box["cx"], box["cy"]
        dx, dy = tx - cx, ty - cy
        hw, hh = box["w"] / 2, box["h"] / 2
        if dx == 0 and dy == 0:
            return cx, cy
        sx = hw / abs(dx) if dx != 0 else 1e9
        sy = hh / abs(dy) if dy != 0 else 1e9
        s = min(sx, sy)
        return cx + dx * s, cy + dy * s

    p1 = edge(a, bx, by)
    p2 = edge(b, ax_, ay)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=C_LINE, lw=1.5,
            zorder=1)
    # кардинальности у концов
    ax.text(p1[0] + (p2[0] - p1[0]) * 0.12, p1[1] + (p2[1] - p1[1]) * 0.12,
            one_a, fontsize=11, ha="center", va="center", color="#000000",
            fontweight="bold", zorder=5,
            bbox=dict(boxstyle="circle,pad=0.1", fc="white", ec="none"))
    ax.text(p2[0] - (p2[0] - p1[0]) * 0.12, p2[1] - (p2[1] - p1[1]) * 0.12,
            one_b, fontsize=11, ha="center", va="center", color="#000000",
            fontweight="bold", zorder=5,
            bbox=dict(boxstyle="circle,pad=0.1", fc="white", ec="none"))
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my, label, fontsize=8, ha="center", va="center",
                color="#000000", style="italic", zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))


def build() -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=160)
    ax.set_xlim(0, 15)
    # Запас сверху: самый высокий блок (user_profiles) доходит до y≈9.24,
    # выше идёт строка легенды, ещё выше — заголовок (две отдельные строки,
    # чтобы ничего не наезжало на таблицы и друг на друга).
    ax.set_ylim(0, 10.9)
    ax.axis("off")

    users = _entity(ax, "users", [
        ("id", "pk"), ("email", ""), ("password_hash", ""),
        ("email_status", ""),
    ], x=0.4, y=4.0, header_style=GRP_AUTH)

    profiles = _entity(ax, "user_profiles", [
        ("id", "pk"), ("user_id", "fk"), ("goal", ""),
        ("training_level", ""), ("frequency", ""), ("equipment", ""),
    ], x=0.4, y=6.9, header_style=GRP_AUTH)

    pdf = _entity(ax, "pdf_import_jobs", [
        ("id", "pk"), ("user_id", "fk"), ("status", ""),
        ("extracted (jsonb)", ""), ("confirmed_meas_id", "fk"),
    ], x=4.3, y=7.0, header_style=GRP_AUTH)

    meas = _entity(ax, "inbody_measurements", [
        ("id", "pk"), ("user_id", "fk"), ("measured_at", ""),
        ("weight_kg", ""), ("body_fat_percent", ""),
        ("muscle_mass_kg", ""), ("bmr_kcal", ""), ("source", ""),
    ], x=4.3, y=3.4, header_style=GRP_AUTH)

    forecasts = _entity(ax, "inbody_forecasts", [
        ("id", "pk"), ("user_id", "fk"), ("based_on_inbody_id", "fk"),
        ("horizon_weeks", ""), ("target_metric", ""),
        ("point_estimate", ""), ("ci_low / ci_high", ""),
        ("confidence", ""), ("model_version", ""),
    ], x=8.6, y=5.0, header_style=GRP_FORECAST)

    evals = _entity(ax, "forecast_evaluations", [
        ("id", "pk"), ("forecast_id", "fk"), ("actual_inbody_id", "fk"),
        ("absolute_error", ""), ("within_ci", ""),
    ], x=11.6, y=0.9, header_style=GRP_FORECAST)

    plans = _entity(ax, "workout_plans", [
        ("id", "pk"), ("user_id", "fk"), ("status", ""),
        ("goal", ""), ("model_version", ""), ("fallback", ""),
    ], x=0.4, y=0.7, header_style=GRP_ADAPT)

    rebuilds = _entity(ax, "plan_rebuild_events", [
        ("id", "pk"), ("user_id", "fk"), ("trigger", ""),
        ("target_plan", ""), ("status", ""),
    ], x=4.3, y=0.9, header_style=GRP_ADAPT)

    # Связи (∞ = много)
    _rel(ax, users, profiles, one_a="1", one_b="1")
    _rel(ax, users, meas, one_a="1", one_b="∞")
    _rel(ax, users, forecasts, one_a="1", one_b="∞")
    _rel(ax, users, plans, one_a="1", one_b="∞")
    _rel(ax, users, rebuilds, one_a="1", one_b="∞")
    _rel(ax, pdf, meas, one_a="1", one_b="1", label="создаёт")
    _rel(ax, forecasts, meas, one_a="∞", one_b="1", label="based_on")
    _rel(ax, evals, forecasts, one_a="1", one_b="1", label="оценивает")
    _rel(ax, evals, meas, one_a="∞", one_b="1", label="actual")
    _rel(ax, rebuilds, plans, one_a="∞", one_b="1", label="перестраивает")

    # Легенда по стилю шапок групп (заголовок не пишем — он есть в подписи
    # рисунка на слайде/в дипломе).
    legend = [
        (GRP_AUTH, "Auth / профиль / замеры"),
        (GRP_FORECAST, "Прогноз (ядро)"),
        (GRP_ADAPT, "Адаптация плана"),
    ]
    # Следующий элемент ставим после фактического конца предыдущей подписи
    # (измеряем ширину текста), иначе длинные строки наезжают на квадрат рядом.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    lx = 0.4
    for (fc, _tc, hatch), text in legend:
        ax.add_patch(FancyBboxPatch((lx, 9.85), 0.3, 0.22,
                     boxstyle="round,pad=0.02", facecolor=fc,
                     edgecolor=C_EDGE, linewidth=0.8, hatch=hatch))
        t = ax.text(lx + 0.42, 9.96, text, fontsize=9, va="center", color="#000000")
        bb = t.get_window_extent(renderer=renderer)
        x_end = inv.transform((bb.x1, bb.y0))[0]
        lx = x_end + 0.7  # следующий квадрат после текста с отступом

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    out_png = HERE / "er-diagram-maria.png"
    fig.savefig(out_png, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    print(f"Wrote: {out_png}")
    return buf


if __name__ == "__main__":
    build()
