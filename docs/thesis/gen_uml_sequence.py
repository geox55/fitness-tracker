"""UML-диаграмма последовательности: запрос прогноза InBody.

Показывает поток вызова прогноза через слои приложения — от экрана
пользователя до ML-модели и БД и обратно. Соответствует реальному пути
в коде: features/forecast (PWA) → api/v1/forecast → domains/forecast/
service → domain/forecast/ml_predictor → БД.

Результат: docs/thesis/uml-sequence-maria.png — для диплома (глава 4,
REST-сервис прогноза) и/или слайда.

Запуск:  python3 docs/thesis/gen_uml_sequence.py
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

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent

# ЧБ (только чёрный/белый, без серого). Обычные участники — белые с чёрной
# рамкой, ML-модель (ядро работы) — чёрная с белым текстом. Вызовы — сплошные
# чёрные стрелки, возвраты — пунктирные чёрные.
C_FILL = "#FFFFFF"
C_FILL_ML = "#000000"
C_TXT = "#000000"
C_TXT_ML = "#FFFFFF"
C_LINE = "#000000"
C_CALL = "#000000"
C_RET = "#000000"

# Жизненные линии: (id, подпись, x, заливка шапки, цвет текста).
# Общий вид: четыре укрупнённых участника без деталей реализации.
LIFELINES = [
    ("user", "Пользователь", 1.6, C_FILL, C_TXT),
    ("app", "Приложение\n(PWA)", 5.6, C_FILL, C_TXT),
    ("api", "Сервер\n(API)", 9.6, C_FILL, C_TXT),
    ("ml", "ML-модель", 13.4, C_FILL_ML, C_TXT_ML),
]
LX = {lid: x for lid, _, x, _, _ in LIFELINES}

TOP = 8.6        # y шапок жизненных линий
START = 7.6      # y первого сообщения
STEP = 0.85      # шаг по вертикали

# Сообщения: (from, to, label, kind)
#   kind: 'call' (сплошная стрелка), 'return' (пунктир)
MESSAGES = [
    ("user", "app", "Запрос прогноза", "call"),
    ("app", "api", "GET /forecast/inbody", "call"),
    ("api", "ml", "Прогноз по замерам", "call"),
    ("ml", "api", "Δ веса, жира, мышц + интервал", "return"),
    ("api", "app", "Результат прогноза", "return"),
    ("app", "user", "График с интервалом", "return"),
]


def build() -> io.BytesIO:
    bottom = START - STEP * (len(MESSAGES) - 1) - 0.5

    # Высоту холста и нижнюю границу привязываем к фактическому контенту: иначе
    # ось тянется до y=0, а сообщения заканчиваются у y≈3 — снизу оставался
    # большой пустой блок, который bbox tight не срезал.
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=160)
    ax.set_xlim(0, 15)
    ax.set_ylim(bottom - 0.35, TOP + 0.7)
    ax.axis("off")

    # Жизненные линии + шапки
    for lid, label, x, fill, txt in LIFELINES:
        ax.plot([x, x], [TOP - 0.45, bottom], color=C_LINE, lw=1.0,
                linestyle=(0, (4, 3)), zorder=1)
        box = FancyBboxPatch((x - 1.05, TOP - 0.45), 2.1, 0.9,
                             boxstyle="round,pad=0.02,rounding_size=0.08",
                             facecolor=fill, edgecolor="#000000", linewidth=1.3,
                             zorder=3)
        ax.add_patch(box)
        ax.text(x, TOP, label, ha="center", va="center", fontsize=12,
                fontweight="bold", color=txt, zorder=4)

    # Сообщения
    y = START
    for src, dst, label, kind in MESSAGES:
        x1, x2 = LX[src], LX[dst]
        if kind == "self":
            # Петля справа от линии
            w = 1.7
            ax.plot([x1, x1 + w, x1 + w, x1], [y, y, y - 0.28, y - 0.28],
                    color=C_CALL, lw=1.4, zorder=2)
            arr = FancyArrowPatch((x1 + w, y - 0.28), (x1 + 0.02, y - 0.28),
                                  arrowstyle="-|>", mutation_scale=12,
                                  color=C_CALL, lw=1.4, zorder=2)
            ax.add_patch(arr)
            ax.text(x1 + w + 0.2, y - 0.14, label, ha="left", va="center",
                    fontsize=8.8, color="#000000", style="italic", zorder=4)
            y -= STEP * 1.25
            continue

        is_ret = kind == "return"
        style = "-|>"
        arr = FancyArrowPatch((x1, y), (x2, y), arrowstyle=style,
                              mutation_scale=14,
                              color=C_RET if is_ret else C_CALL,
                              lw=1.4,
                              linestyle="--" if is_ret else "-",
                              zorder=2)
        ax.add_patch(arr)
        mid = (x1 + x2) / 2
        ax.text(mid, y + 0.14, label, ha="center", va="bottom",
                fontsize=11, color="#000000",
                style="italic" if is_ret else "normal", zorder=4)
        y -= STEP

    # Заголовок и alt-фрагмент не рисуем: схема общая, название идёт подписью
    # рисунка на слайде/в дипломе.
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    out_png = HERE / "uml-sequence-maria.png"
    fig.savefig(out_png, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    print(f"Wrote: {out_png}")
    return buf


if __name__ == "__main__":
    build()
