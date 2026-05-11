"""Unit-тесты pure-helper build_pdf — spec 010 REQ-10/11.

Pure часть: на вход ReportData, на выход PDF-bytes. Проверяем:
- байты валидно начинаются с `%PDF` и заканчиваются `%%EOF`;
- содержание (через pdfplumber.extract_text) включает заголовки выбранных
  секций и не включает выключенные;
- даты/числа из payload отрисованы в PDF (не «потерялись» при сборке).
"""

from __future__ import annotations

import io
from datetime import date

import pdfplumber
import pytest

from app.domain.analytics.pdf_report import (
    GoalProgressSection,
    InBodySeriesSection,
    ProfileSection,
    ReportData,
    WorkoutsSection,
    build_pdf,
)


def _read_pdf_text(pdf_bytes: bytes) -> str:
    """Извлечь весь текст PDF, склеив страницы пробелом — для assert in."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as doc:
        return "\n".join((page.extract_text() or "") for page in doc.pages)


def _minimal_data(**overrides: object) -> ReportData:
    """Готовый ReportData с пустыми секциями — добавляй только то, что нужно
    конкретному тесту, не плодя бойлерплейт."""
    defaults: dict[str, object] = {
        "generated_at": date(2026, 5, 11),
        "period_from": None,
        "period_to": None,
        "profile": None,
        "inbody": None,
        "workouts": None,
        "goal": None,
    }
    defaults.update(overrides)
    return ReportData(**defaults)  # type: ignore[arg-type]


class TestPdfShape:
    def test_returns_valid_pdf_bytes(self) -> None:
        # Магия %PDF в начале и %%EOF в конце — обязательный признак.
        pdf = build_pdf(_minimal_data())
        assert pdf.startswith(b"%PDF-")
        assert pdf.rstrip().endswith(b"%%EOF")

    def test_contains_global_header_and_generated_date(self) -> None:
        pdf = build_pdf(_minimal_data())
        text = _read_pdf_text(pdf)
        assert "Fitness Tracker" in text
        # generated_at печатается в ISO для машинной читаемости отчёта.
        assert "2026-05-11" in text

    def test_period_range_renders_when_set(self) -> None:
        pdf = build_pdf(_minimal_data(
            period_from=date(2026, 1, 1),
            period_to=date(2026, 4, 30),
        ))
        text = _read_pdf_text(pdf)
        assert "2026-01-01" in text
        assert "2026-04-30" in text


class TestProfileSection:
    def test_renders_when_provided(self) -> None:
        # Профиль — без email/PII (REQ-11): только display_name, цель,
        # рост/вес-таргеты опционально.
        pdf = build_pdf(_minimal_data(profile=ProfileSection(
            display_name="Maria L.",
            sex="female",
            age=28,
            height_cm=170.0,
            goal="weight_loss",
            target_weight_kg=68.0,
            target_muscle_kg=None,
        )))
        text = _read_pdf_text(pdf)
        assert "Profile" in text
        assert "Maria L." in text
        assert "weight_loss" in text
        assert "170" in text  # рост
        assert "68" in text  # target_weight_kg

    def test_skipped_section_does_not_appear(self) -> None:
        pdf = build_pdf(_minimal_data(profile=None))
        text = _read_pdf_text(pdf)
        assert "Profile" not in text


class TestInBodySection:
    def test_renders_metric_table_with_dates_and_values(self) -> None:
        pdf = build_pdf(_minimal_data(inbody=InBodySeriesSection(
            weight=[(date(2026, 1, 15), 82.0), (date(2026, 3, 15), 80.5)],
            body_fat_percent=[(date(2026, 1, 15), 24.0), (date(2026, 3, 15), 22.5)],
            muscle_mass_kg=[(date(2026, 1, 15), 30.0), (date(2026, 3, 15), 31.0)],
        )))
        text = _read_pdf_text(pdf)
        assert "InBody" in text
        assert "82" in text
        assert "24" in text
        assert "31" in text

    def test_renders_when_only_one_metric_present(self) -> None:
        # Партиальные замеры: иногда есть вес, нет жира. PDF должен это
        # принимать без падений.
        pdf = build_pdf(_minimal_data(inbody=InBodySeriesSection(
            weight=[(date(2026, 1, 15), 82.0)],
            body_fat_percent=[],
            muscle_mass_kg=[],
        )))
        text = _read_pdf_text(pdf)
        assert "InBody" in text
        assert "82" in text

    def test_empty_section_skipped(self) -> None:
        # Все три метрики пустые → секцию не рисуем, отчёт пустого блока
        # не показывает.
        pdf = build_pdf(_minimal_data(inbody=InBodySeriesSection(
            weight=[], body_fat_percent=[], muscle_mass_kg=[],
        )))
        text = _read_pdf_text(pdf)
        assert "InBody" not in text


class TestWorkoutsSection:
    def test_renders_buckets_table(self) -> None:
        pdf = build_pdf(_minimal_data(workouts=WorkoutsSection(
            bucket="week",
            items=[
                (date(2026, 4, 6), 13920.0, 2),
                (date(2026, 4, 13), 500.0, 1),
            ],
        )))
        text = _read_pdf_text(pdf)
        assert "Workouts" in text
        assert "2026-04-06" in text
        assert "13920" in text or "13 920" in text  # форматирование

    def test_empty_workouts_skipped(self) -> None:
        pdf = build_pdf(_minimal_data(workouts=WorkoutsSection(
            bucket="week", items=[],
        )))
        text = _read_pdf_text(pdf)
        assert "Workouts" not in text


class TestGoalSection:
    def test_renders_goal_progress_with_eta(self) -> None:
        pdf = build_pdf(_minimal_data(goal=GoalProgressSection(
            goal="weight_loss",
            start_value=90.0,
            current_value=84.0,
            target_value=80.0,
            progress_percent=60,
            eta=date(2026, 8, 12),
        )))
        text = _read_pdf_text(pdf)
        assert "Goal" in text
        assert "weight_loss" in text
        assert "60%" in text
        assert "2026-08-12" in text

    def test_goal_without_eta_renders(self) -> None:
        # ETA может не быть (forecast не построился) — это не ошибка.
        pdf = build_pdf(_minimal_data(goal=GoalProgressSection(
            goal="muscle_gain",
            start_value=30.0,
            current_value=32.0,
            target_value=35.0,
            progress_percent=40,
            eta=None,
        )))
        text = _read_pdf_text(pdf)
        assert "Goal" in text
        assert "muscle_gain" in text
        # вместо ETA UI/PDF пишет «—» или «n/a»; ассертим, что нет краша.

    def test_no_goal_section_skipped(self) -> None:
        pdf = build_pdf(_minimal_data(goal=None))
        text = _read_pdf_text(pdf)
        assert "Goal" not in text


class TestEmptyReport:
    def test_all_sections_empty_still_produces_valid_pdf(self) -> None:
        # Edge case: пользователь нажал «экспорт» сразу после регистрации.
        # Не должны падать; PDF просто шапка + «Нет данных».
        pdf = build_pdf(_minimal_data())
        assert pdf.startswith(b"%PDF-")
        text = _read_pdf_text(pdf)
        # Дисклеймер для пустых отчётов — хоть какой-то контент.
        assert "No data" in text or "Fitness Tracker" in text


class TestPageLimit:
    def test_huge_inbody_series_capped_to_max_pages(self) -> None:
        # spec 010 Edge Cases: PDF 100+ страниц обрезается до 50.
        # Даём 5000 точек — гарантированно вышло бы за 50 страниц без
        # ограничения; build_pdf должен сам сократить.
        many = [(date(2026, 1, 1), 80.0 + i * 0.01) for i in range(5000)]
        pdf = build_pdf(_minimal_data(inbody=InBodySeriesSection(
            weight=many, body_fat_percent=[], muscle_mass_kg=[],
        )))
        with pdfplumber.open(io.BytesIO(pdf)) as doc:
            assert len(doc.pages) <= 50


@pytest.mark.parametrize("section_name,builder", [
    ("profile", lambda: ProfileSection(
        display_name="X", sex=None, age=None, height_cm=None,
        goal=None, target_weight_kg=None, target_muscle_kg=None,
    )),
    ("inbody", lambda: InBodySeriesSection(
        weight=[(date(2026, 1, 1), 80.0)],
        body_fat_percent=[], muscle_mass_kg=[],
    )),
    ("workouts", lambda: WorkoutsSection(
        bucket="week", items=[(date(2026, 4, 6), 100.0, 1)],
    )),
    ("goal", lambda: GoalProgressSection(
        goal="weight_loss", start_value=90.0, current_value=85.0,
        target_value=80.0, progress_percent=50, eta=None,
    )),
])
def test_each_section_independently_renders(section_name, builder):  # type: ignore[no-untyped-def]
    # Каждая секция self-contained: рисуется без зависимости от других.
    data = _minimal_data(**{section_name: builder()})
    pdf = build_pdf(data)
    assert pdf.startswith(b"%PDF-")
