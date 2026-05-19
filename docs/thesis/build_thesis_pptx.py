"""Генератор презентаций к защите для Маши и Егора.

Запуск: `uv run --group ml python docs/thesis/build_thesis_pptx.py`

Артефакты: `docs/thesis/presentation-maria.pptx`, `presentation-egor.pptx`.

Структура слайдов (12 на каждого) описана в README; графики метрик
генерируются на лету через matplotlib и встраиваются как изображения.
"""

from __future__ import annotations

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # без GUI-бекенда — для серверной/CI среды
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).parent
SCREENSHOTS = HERE.parent / "design" / "screenshots"

# --- Палитра -----------------------------------------------------------------
NAVY = RGBColor(0x14, 0x1B, 0x2D)        # тёмно-синий фон титула
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT = RGBColor(0x7F, 0x0D, 0xF2)      # primary из дизайн-системы
TEXT_DARK = RGBColor(0x1F, 0x1F, 0x1F)
TEXT_MUTED = RGBColor(0x55, 0x55, 0x55)
DIVIDER = RGBColor(0xE0, 0xE0, 0xE0)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# =============================================================================
# Низкоуровневые хелперы
# =============================================================================


def _new_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def _blank_slide(prs: Presentation):
    """Чистый слайд без layout-плейсхолдеров — мы раскладываем сами."""
    return prs.slides.add_slide(prs.slide_layouts[6])


def _add_textbox(
    slide,
    *,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    font_size: int = 20,
    bold: bool = False,
    color: RGBColor = TEXT_DARK,
    align=PP_ALIGN.LEFT,
    font_name: str = "Calibri",
):
    """Универсальный текст-блок. Координаты в дюймах."""
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def _add_bullets(
    slide,
    *,
    left: float,
    top: float,
    width: float,
    height: float,
    items: list[str],
    font_size: int = 18,
    color: RGBColor = TEXT_DARK,
):
    """Маркированный список. Каждый пункт — один параграф с буллетом «•»."""
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(8)
        run = p.add_run()
        run.text = f"•  {item}"
        run.font.name = "Calibri"
        run.font.size = Pt(font_size)
        run.font.color.rgb = color


def _add_rect(slide, *, left: float, top: float, width: float, height: float, color: RGBColor):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def _add_accent_bar(slide, *, top: float = 0.65):
    """Тонкая фиолетовая полоса под заголовком — общий визуальный якорь."""
    _add_rect(slide, left=0.6, top=top, width=1.2, height=0.06, color=ACCENT)


def _header(slide, title: str):
    """Стандартный заголовок content-слайда."""
    _add_textbox(
        slide,
        left=0.6, top=0.3, width=12.0, height=0.6,
        text=title, font_size=28, bold=True, color=TEXT_DARK,
    )
    _add_accent_bar(slide)


def _footer(slide, page: int, total: int, author_short: str):
    """Подпись «N/M» внизу — помогает комиссии ориентироваться."""
    _add_textbox(
        slide,
        left=0.6, top=7.05, width=6.0, height=0.3,
        text=f"{author_short}  ·  ВКР 2026  ·  Fitness Tracker",
        font_size=10, color=TEXT_MUTED,
    )
    _add_textbox(
        slide,
        left=11.5, top=7.05, width=1.3, height=0.3,
        text=f"{page} / {total}",
        font_size=10, color=TEXT_MUTED, align=PP_ALIGN.RIGHT,
    )


# =============================================================================
# matplotlib-чарты → PNG в memory
# =============================================================================


def _chart_inbody_models() -> io.BytesIO:
    """Сравнение MAE по 3 таргетам для 4 моделей (Маша)."""
    targets = ["Δ weight\n(кг)", "Δ body fat\n(%)", "Δ muscle\n(кг)"]
    persistence = [0.325, 0.276, 0.146]
    ridge = [0.168, 0.243, 0.127]
    lgbm = [0.156, 0.241, 0.120]
    mlp = [0.156, 0.238, 0.121]

    import numpy as np
    x = np.arange(len(targets))
    w = 0.2

    fig, ax = plt.subplots(figsize=(10, 5), dpi=160)
    bars = [
        ("Persistence (baseline)", persistence, "#BDBDBD"),
        ("Ridge", ridge, "#9E9E9E"),
        ("LightGBM (прод)", lgbm, "#7F0DF2"),
        ("MLP (PyTorch)", mlp, "#5C0CB4"),
    ]
    for i, (name, vals, color) in enumerate(bars):
        ax.bar(x + (i - 1.5) * w, vals, w, label=name, color=color, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(targets, fontsize=11)
    ax.set_ylabel("MAE (меньше — лучше)", fontsize=11)
    ax.set_title("Сравнение моделей: точность на тестовом сплите (1467 точек)",
                 fontsize=13, pad=15)
    ax.legend(loc="upper right", fontsize=10, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _chart_workout_models() -> io.BytesIO:
    """Сравнение ROC-AUC для popularity / LR / LGBM (Егор)."""
    models = ["Popularity\n(baseline)", "Logistic\nRegression", "LightGBM\n(прод)"]
    roc_auc = [0.500, 0.939, 0.985]
    colors = ["#BDBDBD", "#9E9E9E", "#7F0DF2"]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=160)
    bars = ax.bar(models, roc_auc, color=colors, edgecolor="white", width=0.55)
    ax.set_ylim(0.4, 1.05)
    ax.set_ylabel("ROC-AUC (больше — лучше)", fontsize=11)
    ax.set_title("Сравнение моделей ранжирования упражнений",
                 fontsize=13, pad=15)
    for b, v in zip(bars, roc_auc):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.3f}",
                ha="center", fontsize=12, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _chart_ci_coverage() -> io.BytesIO:
    """Калибровка доверительных интервалов: фактический coverage vs теоретический 80%."""
    targets = ["Δ weight", "Δ body fat", "Δ muscle"]
    lgbm = [0.79, 0.78, 0.80]
    mlp = [0.83, 0.79, 0.83]
    target_line = 0.80

    import numpy as np
    x = np.arange(len(targets))
    w = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=160)
    ax.bar(x - w / 2, lgbm, w, label="LightGBM", color="#7F0DF2", edgecolor="white")
    ax.bar(x + w / 2, mlp, w, label="MLP", color="#5C0CB4", edgecolor="white")
    ax.axhline(y=target_line, color="#22C55E", linestyle="--", linewidth=2,
               label="Теоретический уровень 80%")
    ax.set_xticks(x)
    ax.set_xticklabels(targets, fontsize=11)
    ax.set_ylabel("Доля точек в [q10, q90]", fontsize=11)
    ax.set_ylim(0.60, 0.95)
    ax.set_title("Калибровка 80%-доверительных интервалов",
                 fontsize=13, pad=15)
    ax.legend(loc="lower right", fontsize=10, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# =============================================================================
# Слайд-конструкторы
# =============================================================================


def slide_title(prs: Presentation, *, topic: str, author: str, group: str,
                supervisor: str = "Симанчев Р. Ю., канд. физ.-мат. наук, доцент"):
    """Титульный слайд: тёмный фон, тема, ФИО."""
    s = _blank_slide(prs)
    _add_rect(s, left=0, top=0, width=13.333, height=7.5, color=NAVY)
    _add_rect(s, left=0.6, top=3.3, width=1.5, height=0.08, color=ACCENT)

    _add_textbox(s, left=0.6, top=0.7, width=12.0, height=0.5,
                 text="Омский государственный университет им. Ф. М. Достоевского",
                 font_size=14, color=WHITE)
    _add_textbox(s, left=0.6, top=1.05, width=12.0, height=0.5,
                 text="Факультет цифровых технологий, кибербезопасности, математики и технологий",
                 font_size=12, color=RGBColor(0xBB, 0xBB, 0xBB))

    _add_textbox(s, left=0.6, top=1.9, width=12.0, height=0.4,
                 text="ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА",
                 font_size=14, color=ACCENT, bold=True)
    _add_textbox(s, left=0.6, top=2.3, width=12.0, height=0.4,
                 text="«Прикладная математика и информатика» · магистратура",
                 font_size=12, color=RGBColor(0xBB, 0xBB, 0xBB))

    _add_textbox(s, left=0.6, top=3.5, width=12.0, height=2.0,
                 text=topic, font_size=26, bold=True, color=WHITE)

    _add_textbox(s, left=0.6, top=5.7, width=6.0, height=0.4,
                 text="Автор:", font_size=12, color=RGBColor(0xBB, 0xBB, 0xBB))
    _add_textbox(s, left=0.6, top=6.0, width=6.0, height=0.4,
                 text=f"{author}, гр. {group}", font_size=16, color=WHITE, bold=True)

    _add_textbox(s, left=7.0, top=5.7, width=6.0, height=0.4,
                 text="Научный руководитель:",
                 font_size=12, color=RGBColor(0xBB, 0xBB, 0xBB))
    _add_textbox(s, left=7.0, top=6.0, width=6.0, height=0.6,
                 text=supervisor, font_size=14, color=WHITE)

    _add_textbox(s, left=0.6, top=6.9, width=12.0, height=0.4,
                 text="Омск · 2026", font_size=12,
                 color=RGBColor(0xBB, 0xBB, 0xBB))


def slide_relevance(prs, *, page, total, author_short, intro: str, points: list[str]):
    s = _blank_slide(prs)
    _header(s, "Актуальность")
    _add_textbox(s, left=0.6, top=1.1, width=12.0, height=0.8,
                 text=intro, font_size=18, color=TEXT_DARK)
    _add_bullets(s, left=0.6, top=2.3, width=12.0, height=4.5, items=points,
                 font_size=18)
    _footer(s, page, total, author_short)


def slide_goal_tasks(prs, *, page, total, author_short, goal: str, tasks: list[str]):
    s = _blank_slide(prs)
    _header(s, "Цель и задачи")
    _add_textbox(s, left=0.6, top=1.1, width=2.5, height=0.4,
                 text="Цель", font_size=16, bold=True, color=ACCENT)
    _add_textbox(s, left=0.6, top=1.5, width=12.0, height=1.2,
                 text=goal, font_size=18, color=TEXT_DARK)
    _add_textbox(s, left=0.6, top=2.9, width=4.0, height=0.4,
                 text="Задачи", font_size=16, bold=True, color=ACCENT)
    _add_bullets(s, left=0.6, top=3.3, width=12.0, height=3.5, items=tasks,
                 font_size=16)
    _footer(s, page, total, author_short)


def slide_architecture(prs, *, page, total, author_short, points: list[str], stack: list[str]):
    s = _blank_slide(prs)
    _header(s, "Архитектура приложения")
    _add_textbox(s, left=0.6, top=1.1, width=6.0, height=0.4,
                 text="Принципы", font_size=14, bold=True, color=ACCENT)
    _add_bullets(s, left=0.6, top=1.5, width=6.0, height=4.5, items=points,
                 font_size=14)
    _add_textbox(s, left=7.0, top=1.1, width=6.0, height=0.4,
                 text="Стек", font_size=14, bold=True, color=ACCENT)
    _add_bullets(s, left=7.0, top=1.5, width=6.0, height=4.5, items=stack,
                 font_size=14)
    _footer(s, page, total, author_short)


def slide_content(prs, *, page, total, author_short, title: str, items: list[str],
                  intro: str | None = None):
    s = _blank_slide(prs)
    _header(s, title)
    top = 1.1
    if intro:
        _add_textbox(s, left=0.6, top=top, width=12.0, height=0.8,
                     text=intro, font_size=18, color=TEXT_DARK)
        top = 2.2
    _add_bullets(s, left=0.6, top=top, width=12.0, height=7.5 - top - 0.5,
                 items=items, font_size=17)
    _footer(s, page, total, author_short)


def slide_chart(prs, *, page, total, author_short, title: str, chart: io.BytesIO,
                caption: str | None = None):
    s = _blank_slide(prs)
    _header(s, title)
    s.shapes.add_picture(chart, Inches(1.2), Inches(1.1),
                         width=Inches(11.0))
    if caption:
        _add_textbox(s, left=0.6, top=6.4, width=12.0, height=0.5,
                     text=caption, font_size=14, color=TEXT_MUTED, align=PP_ALIGN.CENTER)
    _footer(s, page, total, author_short)


def slide_screenshots(prs, *, page, total, author_short, title: str,
                      shots: list[tuple[Path, str]]):
    """До 3 скриншотов в ряд с подписями."""
    s = _blank_slide(prs)
    _header(s, title)
    n = len(shots)
    total_w = 11.5
    gap = 0.3
    each_w = (total_w - gap * (n - 1)) / n
    each_h = 4.8
    start_left = (13.333 - total_w) / 2

    for i, (path, caption) in enumerate(shots):
        left = start_left + i * (each_w + gap)
        try:
            s.shapes.add_picture(str(path), Inches(left), Inches(1.2),
                                 width=Inches(each_w), height=Inches(each_h))
        except Exception:
            _add_rect(s, left=left, top=1.2, width=each_w, height=each_h, color=DIVIDER)
        _add_textbox(s, left=left, top=6.15, width=each_w, height=0.6,
                     text=caption, font_size=12, color=TEXT_MUTED,
                     align=PP_ALIGN.CENTER)
    _footer(s, page, total, author_short)


def slide_conclusion(prs, *, page, total, author_short, items: list[str]):
    s = _blank_slide(prs)
    _header(s, "Выводы")
    _add_bullets(s, left=0.6, top=1.2, width=12.0, height=5.5, items=items,
                 font_size=18)
    _footer(s, page, total, author_short)


def slide_thanks(prs, *, author: str):
    """Финальный слайд — большое «Спасибо», ФИО, контакт."""
    s = _blank_slide(prs)
    _add_rect(s, left=0, top=0, width=13.333, height=7.5, color=NAVY)
    _add_textbox(s, left=0.6, top=2.5, width=12.0, height=1.5,
                 text="Спасибо за внимание",
                 font_size=54, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    _add_rect(s, left=6.0, top=4.0, width=1.3, height=0.08, color=ACCENT)
    _add_textbox(s, left=0.6, top=4.4, width=12.0, height=0.6,
                 text="Готова ответить на вопросы",
                 font_size=20, color=RGBColor(0xBB, 0xBB, 0xBB), align=PP_ALIGN.CENTER)
    _add_textbox(s, left=0.6, top=5.5, width=12.0, height=0.5,
                 text=author, font_size=16, color=WHITE, align=PP_ALIGN.CENTER)
    _add_textbox(s, left=0.6, top=5.95, width=12.0, height=0.4,
                 text="Омск · 2026", font_size=12,
                 color=RGBColor(0xBB, 0xBB, 0xBB), align=PP_ALIGN.CENTER)


# =============================================================================
# СБОРКА: Маша (12 слайдов)
# =============================================================================


def build_maria() -> Path:
    prs = _new_prs()
    total = 12
    short = "Лапова М. И."

    # 1. Титул
    slide_title(
        prs,
        topic="Разработка кроссплатформенного приложения "
              "для прогноза состава тела и адаптации плана тренировок "
              "с использованием машинного обучения",
        author="Лапова Мария Игоревна",
        group="МММ-401-О-03",
    )

    # 2. Актуальность
    slide_relevance(
        prs, page=2, total=total, author_short=short,
        intro="Самостоятельные силовые тренировки требуют системного "
              "контроля состава тела и своевременной адаптации плана.",
        points=[
            "Биоимпедансный анализ (InBody) даёт точные показатели состава тела, "
            "но интерпретация требует экспертизы тренера",
            "Существующие приложения (Hevy, Strong, Fitbod) ведут дневник тренировок, "
            "но не прогнозируют изменения состава тела на 1–4 недели вперёд",
            "Пользователь без знания физиологии не может оценить, насколько "
            "его тренировки и питание соответствуют цели",
            "Решение: ML-модель прогноза + детерминированный сервис автоматической "
            "адаптации тренировочного плана при изменениях профиля",
        ],
    )

    # 3. Цель и задачи
    slide_goal_tasks(
        prs, page=3, total=total, author_short=short,
        goal="Разработать кроссплатформенное приложение с прогнозом "
             "InBody-метрик на горизонт 1–4 недели и автоматической "
             "адаптацией плана тренировок.",
        tasks=[
            "Проанализировать существующие фитнес-приложения и подходы к "
            "прогнозу динамики веса и состава тела",
            "Спроектировать архитектуру PWA-приложения (FastAPI + Flutter + PostgreSQL)",
            "Собрать датасет временных рядов InBody с синтезом траекторий из "
            "открытых Kaggle-источников",
            "Обучить и сравнить четыре модели прогноза: persistence, Ridge, "
            "LightGBM quantile, MLP с δ-параметризацией",
            "Реализовать watcher-сервис автоматической адаптации плана при "
            "изменениях профиля пользователя",
            "Покрыть критические компоненты автотестами; обеспечить fallback "
            "на baseline при отказе ML-инференса",
        ],
    )

    # 4. Архитектура
    slide_architecture(
        prs, page=4, total=total, author_short=short,
        points=[
            "Чёткое разделение domain/ (чистая логика, без I/O) и "
            "domains/ (БД-обвязка, FastAPI-роутеры)",
            "Спека-ориентированная разработка: каждая фича закреплена "
            "в specs/NNN-*.md, REQ-теги цитируются в коде",
            "Lazy-load ML-артефактов, безусловный fallback на OLS-baseline "
            "при отсутствии или ошибке модели (REQ-12 spec 008)",
            "Async SQLAlchemy 2 + Alembic-миграции с инкрементной нумерацией",
            "Версионирование ML-моделей: ml/models/<task>/<algo>/v<semver>/",
        ],
        stack=[
            "Backend: FastAPI + SQLAlchemy 2 (async) + PostgreSQL 16",
            "ML: LightGBM, PyTorch, scikit-learn, joblib",
            "Frontend: Flutter (Web/PWA) + Riverpod + go_router + Dio",
            "Storage: MinIO/S3 (signed URLs для приватных файлов)",
            "Инфраструктура: Docker Compose, Alembic, GitHub Actions",
            "Тесты: pytest + testcontainers PostgreSQL",
        ],
    )

    # 5. Модель прогноза
    slide_content(
        prs, page=5, total=total, author_short=short,
        title="Двухуровневая модель прогноза InBody",
        intro="Задача: предсказать Δ веса, Δ % жира, Δ мышечной массы "
              "на горизонте 1, 2, 4 недели с доверительными интервалами.",
        items=[
            "Постановка: квантильная one-step регрессия дельт; "
            "multi-horizon получается рекурсивным применением модели",
            "Целевая функция quantile (α ∈ {0.1, 0.5, 0.9}) даёт три "
            "оценки: нижняя граница CI, медиана (точечный прогноз), верхняя граница",
            "12 признаков: возраст, пол, рост, текущие weight/fat/muscle, "
            "BMI, FFM, тренировочный объём, калории, цель (one-hot)",
            "Baseline для сравнения: persistence (Δ=0) и Ridge — обязательны для "
            "проверки, что ML-модель несёт полезный сигнал",
            "Альтернативная архитектура: MLP с shared trunk 64→32 + per-target "
            "heads + δ-параметризация (гарантирует q10 ≤ q50 ≤ q90)",
        ],
    )

    # 6. Датасет
    slide_content(
        prs, page=6, total=total, author_short=short,
        title="Датасет: 9776 точек, синтез траекторий",
        intro="Открытых time-series датасетов InBody не существует. Решение — "
              "синтез траекторий на основе двух кросс-секционных Kaggle-источников.",
        items=[
            "S3 (gym-members-exercise-dataset): 973 строки профилей фитнес-клиентов "
            "после prevalence-фильтрации",
            "S4 (body-fat-prediction-dataset): 251 строка с body composition",
            "Синтез: для каждого пользователя из S3 генерируется 8-недельная "
            "траектория с физиологически правдоподобной динамикой",
            "Итог: 9776 строк (пользователь × неделя), 1222 анонимизированных "
            "пользователя; флаг is_synthetic=True",
            "Сплит 70/15/15 без leakage по anon_user_id: 6843 / 1466 / 1467 точек",
            "Воспроизводимость: SHA-256 датасета фиксируется в manifest.json "
            "каждой модели; seed=42 на всех шагах",
        ],
    )

    # 7. Сравнение моделей (chart)
    slide_chart(
        prs, page=7, total=total, author_short=short,
        title="Сравнение моделей: MAE на тестовом сплите",
        chart=_chart_inbody_models(),
        caption="LightGBM выбран в качестве прод-модели: бьёт baseline'ы на всех "
                "трёх таргетах, R²(weight)=0.73, скорость инференса < 50 мс.",
    )

    # 8. Watcher-сервис
    slide_content(
        prs, page=8, total=total, author_short=short,
        title="Watcher-сервис адаптации плана",
        intro="Детерминированный сервис, реагирующий на изменения профиля "
              "и истории тренировок без участия пользователя.",
        items=[
            "6 условий срабатывания: изменение веса, цели, частоты, оборудования, "
            "окончание цикла, ручной запуск",
            "Architecture: pg-cron + watcher-функции в domain/-слое; "
            "идемпотентность по pending-событиям",
            "При срабатывании создаётся PlanRebuildEvent в БД; пересборка плана "
            "происходит асинхронно через BackgroundTasks",
            "Покрытие тестами: 8 модульных + 11 интеграционных, "
            "включая race-conditions между триггерами",
            "Гарантия консистентности: одно активное событие на пользователя "
            "(partial unique index)",
        ],
    )

    # 9. Тестирование
    slide_content(
        prs, page=9, total=total, author_short=short,
        title="Тестирование",
        intro="Многоуровневая стратегия: чистые юниты на domain/-слое + "
              "интеграционные тесты с реальным PostgreSQL.",
        items=[
            "Юнит-тесты domain/: 49 тестов forecast/ML-слоя (composer, baseline, "
            "features, interpretation, evaluation)",
            "Интеграционные тесты: testcontainers Postgres + savepoint per test; "
            "FastAPI берёт ту же сессию через dependency_overrides",
            "ML-pipeline: smoke-тесты обучения для persistence / Ridge / LightGBM "
            "на mini-датасете (изоляция через tmp_path)",
            "Калибровка CI на тестовом сплите: 0.78–0.80 для LGBM, 0.79–0.83 для MLP "
            "(теоретический уровень — 0.80)",
            "Маркеры pytest unit / integration проставляются автоматически по пути; "
            "make check = lint + typecheck (strict mypy) + test",
        ],
    )

    # 10. UI (скриншоты)
    slide_screenshots(
        prs, page=10, total=total, author_short=short,
        title="Интерфейс приложения",
        shots=[
            (SCREENSHOTS / "screen-03.png",
             "Главный экран: прогресс веса и активность"),
            (SCREENSHOTS / "screen-05.png",
             "Лог тренировки: подходы, веса, прогрессия"),
            (SCREENSHOTS / "screen-01.png",
             "Регистрация и онбординг пользователя"),
        ],
    )

    # 11. Выводы
    slide_conclusion(
        prs, page=11, total=total, author_short=short,
        items=[
            "Реализовано кроссплатформенное PWA-приложение с end-to-end "
            "интеграцией ML-моделей в продакшен (FastAPI + Flutter)",
            "Обучены и сравнены 4 модели прогноза InBody; LightGBM quantile "
            "обеспечивает R²=0.73 на Δ weight и калиброванный 80%-CI (0.79)",
            "Реализован watcher-сервис автоматической адаптации плана по 6 "
            "условиям срабатывания, покрыт 19 тестами",
            "Подтверждена гипотеза: квантильная регрессия даёт точный прогноз "
            "с адекватной калибровкой; снижение MAE на Δ weight 52% vs persistence",
            "Архитектура спроектирована с расчётом на отказоустойчивость: "
            "fallback на OLS-baseline при отсутствии ML-артефакта",
        ],
    )

    # 12. Спасибо
    slide_thanks(prs, author="Лапова Мария Игоревна · группа МММ-401-О-03")

    out = HERE / "presentation-maria.pptx"
    prs.save(out)
    return out


# =============================================================================
# СБОРКА: Егор (12 слайдов)
# =============================================================================


def build_egor() -> Path:
    prs = _new_prs()
    total = 12
    short = "Лазарев Е. Д."

    # 1. Титул
    slide_title(
        prs,
        topic="Разработка кроссплатформенного приложения "
              "для автоматической генерации планов тренировок "
              "с использованием машинного обучения",
        author="Лазарев Егор Дмитриевич",
        group="МММ-401-О-03",
    )

    # 2. Актуальность
    slide_relevance(
        prs, page=2, total=total, author_short=short,
        intro="Самостоятельные тренировки без программы — основная причина "
              "плато и отсутствия прогресса у новичков и любителей.",
        points=[
            "Существующие фитнес-приложения либо ведут дневник без генерации "
            "программ (Hevy, Strong), либо предлагают шаблонные планы (Fitbod, Caliber)",
            "Универсальные программы не учитывают цель, уровень, частоту, доступное "
            "оборудование и динамику пользователя",
            "Чистый rule-based — однообразен; чистое ML — требует десятков тысяч пар "
            "(профиль, программа), которых нет в открытом доступе",
            "Решение: гибридный алгоритм — ML-ранкер упражнений + детерминированный "
            "composer, гарантирующий корректность сборки плана",
        ],
    )

    # 3. Цель и задачи
    slide_goal_tasks(
        prs, page=3, total=total, author_short=short,
        goal="Разработать кроссплатформенное приложение для автоматической "
             "генерации индивидуальных тренировочных программ на основе ML.",
        tasks=[
            "Проанализировать существующие подходы к генерации тренировочных "
            "программ (rule-based, end-to-end ML, рекомендательные системы)",
            "Сформировать обучающий датасет из 97 760 пар (профиль, упражнение, "
            "метка) на основе Kaggle-источника и rule-based разметки",
            "Обучить и сравнить три модели ранжирования: popularity-baseline, "
            "Logistic Regression, LightGBM Classifier",
            "Реализовать composer — детерминированный сборщик программы из "
            "ранжированного каталога с проверкой тренировочных принципов",
            "Спроектировать REST-сервис генерации с lazy-load ML-артефакта и "
            "rule-based fallback при отсутствии модели",
            "Покрыть критические компоненты автотестами; обеспечить версионирование "
            "моделей и воспроизводимость пайплайна",
        ],
    )

    # 4. Архитектура
    slide_architecture(
        prs, page=4, total=total, author_short=short,
        points=[
            "Гибридная схема ML + rules: ранкер ранжирует, composer гарантирует "
            "корректность (сплит на день/неделю, разнообразие, объём)",
            "Spec-driven разработка: spec 006 фиксирует требования к генератору, "
            "spec 012 — к ML-пайплайну",
            "Lazy-load ранкера с lru_cache; rule-based fallback при отсутствии "
            "или ошибке инференса — без видимого сбоя для пользователя",
            "Domain/-слой принимает ExercisePool dataclass'ы, возвращает PlannedPlan "
            "без I/O — изолированные unit-тесты на сложной логике composer'а",
            "Версионирование артефактов: ml/models/workout_rec/<algo>/v<semver>/",
        ],
        stack=[
            "Backend: FastAPI + SQLAlchemy 2 (async) + PostgreSQL 16",
            "ML: LightGBM, scikit-learn, pandas, joblib",
            "Frontend: Flutter (Web/PWA) + Riverpod + go_router + Dio",
            "Pipeline: ml/etl/workout_recommender/ + ml/training/workout_recommender/",
            "Инфраструктура: Docker Compose, Alembic-миграции, GitHub Actions",
            "Тесты: pytest + testcontainers PostgreSQL",
        ],
    )

    # 5. Алгоритм
    slide_content(
        prs, page=5, total=total, author_short=short,
        title="Гибридный алгоритм: ML-ранкер + composer",
        intro="Двухстадийная схема: ML сначала ранжирует, потом детерминированные "
              "правила собирают валидный план.",
        items=[
            "Стадия 1 (ML): LightGBM Classifier выдаёт score = P(упражнение "
            "подходит профилю); ранжирование каталога по этим score",
            "Стадия 2 (composer): обход ранжированного каталога с проверкой "
            "сплита (push/pull/legs), оборудования, баланса compound/isolation",
            "Алгоритм прогрессии: на каждой неделе цикла — увеличение веса/повторов "
            "по правилам линейной/двойной прогрессии",
            "Fallback path: при отсутствии ML-артефакта composer использует "
            "rule-based score (тот же интерфейс ExercisePool)",
            "Выход — иерархия workout_plan → plan_weeks → plan_days → plan_exercises, "
            "сохраняется в БД в одной транзакции",
        ],
    )

    # 6. Датасет
    slide_content(
        prs, page=6, total=total, author_short=short,
        title="Датасет: 97 760 пар user × exercise",
        intro="Открытых датасетов «профиль пользователя → подходящие упражнения» "
              "нет. Решение — программная разметка через rule-based labels.",
        items=[
            "Источник профилей: Kaggle gym-members-exercise-dataset "
            "(973 строки после фильтрации)",
            "Каталог упражнений: 100+ упражнений из API Ninjas + дополнения, "
            "разнесены по группам мышц / типу / оборудованию",
            "Разметка: для каждой пары (профиль, упражнение) применяются "
            "фиксированные правила → бинарная метка «рекомендуется/нет»",
            "Итог: 97 760 пар; сплит 70/15/15 без leakage по anon_user_id — "
            "68 432 train / 14 664 val / 14 664 test",
            "Воспроизводимость: SHA-256 датасета фиксируется в manifest.json; "
            "правила разметки версионированы вместе со скриптом ETL",
        ],
    )

    # 7. Сравнение моделей (chart)
    slide_chart(
        prs, page=7, total=total, author_short=short,
        title="Сравнение моделей ранжирования",
        chart=_chart_workout_models(),
        caption="LightGBM выбран в качестве прод-модели: ROC-AUC=0.985, "
                "PR-AUC=0.993, P@8=0.99 на тестовом сплите 14 664 пар.",
    )

    # 8. Composer
    slide_content(
        prs, page=8, total=total, author_short=short,
        title="Composer: детерминированная сборка плана",
        intro="Чистая функция в domain/-слое: принимает ExercisePool + ML-scores, "
              "возвращает PlannedPlan без обращений к БД.",
        items=[
            "Вход: каталог упражнений с rule-based score и опционально ML-scores; "
            "профиль пользователя; параметры цикла (4 недели по умолчанию)",
            "Шаг 1: сплит на дни недели по принципу push/pull/legs (или fullbody "
            "при частоте < 4 в неделю)",
            "Шаг 2: обход ранжированного каталога с гарантиями — баланс compound/isolation, "
            "разнообразие групп мышц, соответствие оборудованию",
            "Шаг 3: прогрессия — линейная по неделям цикла с deload-неделей "
            "при необходимости (REQ-08 spec 006)",
            "Изоляция от БД: composer тестируется чистыми unit-тестами без "
            "PostgreSQL, что даёт быстрый CI и простоту дебага",
        ],
    )

    # 9. Тестирование
    slide_content(
        prs, page=9, total=total, author_short=short,
        title="Тестирование",
        intro="Двухуровневая стратегия: domain/-юниты + интеграционные тесты "
              "плюс smoke-тест ML-пайплайна.",
        items=[
            "Composer: чистые unit-тесты без БД — проверки сплита, "
            "разнообразия, прогрессии, fallback'а",
            "Интеграционные тесты: testcontainers Postgres + savepoint per test, "
            "проверка end-to-end POST /api/v1/plans/generate",
            "ML-pipeline: smoke-тесты обучения popularity / LR / LightGBM на "
            "mini-датасете; проверка артефактов и manifest.json",
            "Тесты обработки граничных случаев: профиль не заполнен, оборудование "
            "не выбрано, ML-артефакт недоступен (fallback path)",
            "make check = lint (ruff) + typecheck (strict mypy на src/) + test; "
            "CI-проверка через GitHub Actions на каждый push",
        ],
    )

    # 10. UI (скриншоты)
    slide_screenshots(
        prs, page=10, total=total, author_short=short,
        title="Интерфейс приложения",
        shots=[
            (SCREENSHOTS / "screen-07.png",
             "Каталог упражнений с рекомендациями"),
            (SCREENSHOTS / "screen-08.png",
             "Активная тренировка по сгенерированному плану"),
            (SCREENSHOTS / "screen-04.png",
             "Обзор: статистика и история тренировок"),
        ],
    )

    # 11. Выводы
    slide_conclusion(
        prs, page=11, total=total, author_short=short,
        items=[
            "Реализовано кроссплатформенное PWA-приложение с end-to-end "
            "интеграцией ML-генератора планов в продакшен",
            "Сформирован датасет 97 760 пар user × exercise с rule-based разметкой; "
            "обучены и сравнены 3 модели ранжирования",
            "LightGBM Classifier обеспечивает ROC-AUC=0.985, PR-AUC=0.993 — "
            "превосходит LR (0.939) и popularity-baseline (0.500)",
            "Реализован composer — детерминированный сборщик плана, "
            "гарантирующий корректность независимо от ML-скоров",
            "Архитектура спроектирована с расчётом на отказоустойчивость: "
            "rule-based fallback при отсутствии ML-артефакта",
        ],
    )

    # 12. Спасибо
    slide_thanks(prs, author="Лазарев Егор Дмитриевич · группа МММ-401-О-03")

    out = HERE / "presentation-egor.pptx"
    prs.save(out)
    return out


if __name__ == "__main__":
    maria = build_maria()
    egor = build_egor()
    print(f"Wrote: {maria}")
    print(f"Wrote: {egor}")
