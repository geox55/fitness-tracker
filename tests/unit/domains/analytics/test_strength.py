"""Unit-тесты strength-progress: чистая часть _build_strength_progress."""

from datetime import date

from app.domains.analytics.service import _build_strength_progress


class TestBuildStrengthProgress:
    def test_empty_rows_return_none(self) -> None:
        # Нет логов в окне → блок не рисуется (UI скрывает).
        assert (
            _build_strength_progress(
                title="x", rows=[], window_start=date(2026, 4, 1)
            )
            is None
        )

    def test_day_offset_relative_to_window_start(self) -> None:
        rows = [
            (date(2026, 4, 1), 60.0),  # offset 0
            (date(2026, 4, 8), 65.0),  # offset 7
            (date(2026, 4, 15), 70.0),  # offset 14
        ]
        result = _build_strength_progress(
            title="Squat", rows=rows, window_start=date(2026, 4, 1)
        )
        assert result is not None
        assert [p.day_offset for p in result.points] == [0, 7, 14]
        assert [p.weight_kg for p in result.points] == [60.0, 65.0, 70.0]

    def test_current_max_is_overall_max_in_window(self) -> None:
        # Не последний день, а max за окно — чтобы плато не "обнуляло" PR.
        rows = [
            (date(2026, 4, 1), 60.0),
            (date(2026, 4, 8), 80.0),  # пик
            (date(2026, 4, 15), 70.0),
        ]
        result = _build_strength_progress(
            title="Squat", rows=rows, window_start=date(2026, 4, 1)
        )
        assert result is not None
        assert result.current_max_kg == 80

    def test_max_kg_rounded_half_up(self) -> None:
        rows = [(date(2026, 4, 1), 80.5)]
        result = _build_strength_progress(
            title="Squat", rows=rows, window_start=date(2026, 4, 1)
        )
        assert result is not None
        # round(80.5) → 80 в банковском округлении Python; используем int(round(...)).
        # Главное: возврат — целое число.
        assert isinstance(result.current_max_kg, int)

    def test_title_can_be_none(self) -> None:
        # Если у упражнения нет имени_ru/имени — отдадим None, UI справится.
        rows = [(date(2026, 4, 1), 60.0)]
        result = _build_strength_progress(
            title=None, rows=rows, window_start=date(2026, 4, 1)
        )
        assert result is not None
        assert result.exercise_title is None
