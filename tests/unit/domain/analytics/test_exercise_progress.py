"""Unit-тесты pure-helpers exercise-progress — spec 010 §3 Scenario 4 / REQ-09.

`epley_1rm` и `build_exercise_progress` работают на сырых тапл-строках
вида (date, weight_kg, reps), которые сервис достаёт из БД, и собирают
агрегаты по ISO-неделям. Тесты на них тут — без БД, без ORM.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.domain.analytics.exercise_progress import (
    ExerciseProgressWeek,
    build_exercise_progress,
    epley_1rm,
)


class TestEpley1RM:
    def test_one_rep_formula_returns_103_33_for_100kg(self) -> None:
        # Чистая формула Эпли: `w * (1 + r/30)` — для r=1 это даёт
        # `100 * 31/30 ≈ 103.33`. Это известный артефакт оригинальной
        # формулы (Brzycki/Lombardi не делают такого); мы оставляем
        # как есть, потому что Эпли — самый ходовой вариант в индустрии
        # и спека прямо называет его.
        assert epley_1rm(weight_kg=100.0, reps=1) == pytest.approx(
            103.33, abs=0.01
        )

    def test_classic_5x100_gives_one_rep_max_approx_116(self) -> None:
        # 100 кг × 5 = 1RM ≈ 116.67 (классическая сверка с табличной).
        assert epley_1rm(weight_kg=100.0, reps=5) == pytest.approx(
            116.67, abs=0.01
        )

    def test_high_reps_estimate_grows_linearly_with_reps(self) -> None:
        # 70 × 10 → 70 * (1 + 10/30) = 70 * 4/3 ≈ 93.33
        assert epley_1rm(weight_kg=70.0, reps=10) == pytest.approx(
            93.33, abs=0.01
        )

    def test_zero_reps_raises(self) -> None:
        # 0 повторов — не валидный лог; формула делила бы на 30 безболезненно,
        # но семантически это «упражнение не выполнено», такого в ExerciseLog
        # быть не должно (CHECK reps BETWEEN 1 AND 200). Защищаем helper.
        with pytest.raises(ValueError, match="reps must be ≥ 1"):
            epley_1rm(weight_kg=100.0, reps=0)

    def test_negative_weight_raises(self) -> None:
        with pytest.raises(ValueError, match="weight_kg must be ≥ 0"):
            epley_1rm(weight_kg=-1.0, reps=5)


class TestBuildExerciseProgress:
    def test_empty_rows_returns_empty_list(self) -> None:
        # Нет логов в окне → UI получает пустой массив и сам рисует empty state.
        # Возвращаем именно [], а не None: схема ответа единая.
        assert build_exercise_progress(rows=[]) == []

    def test_groups_rows_by_iso_week(self) -> None:
        # 2026-04-06 — понедельник 15-й ISO-недели; 2026-04-13 — 16-й.
        rows = [
            (date(2026, 4, 6), 100.0, 5),
            (date(2026, 4, 8), 100.0, 5),  # та же неделя
            (date(2026, 4, 13), 105.0, 5),  # следующая неделя
        ]
        weeks = build_exercise_progress(rows=rows)
        assert len(weeks) == 2
        assert weeks[0].week_start == date(2026, 4, 6)
        assert weeks[1].week_start == date(2026, 4, 13)

    def test_week_start_is_monday(self) -> None:
        # ISO-неделя начинается с понедельника независимо от первой даты в ней:
        # лог в среду 2026-04-08 → неделя стартует с 2026-04-06.
        rows = [(date(2026, 4, 8), 80.0, 5)]
        weeks = build_exercise_progress(rows=rows)
        assert weeks[0].week_start == date(2026, 4, 6)

    def test_best_weight_is_max_in_week(self) -> None:
        rows = [
            (date(2026, 4, 6), 100.0, 5),
            (date(2026, 4, 7), 105.0, 3),  # рабочий PR
            (date(2026, 4, 8), 95.0, 8),
        ]
        weeks = build_exercise_progress(rows=rows)
        assert weeks[0].best_weight_kg == 105.0

    def test_best_e1rm_is_max_epley_in_week(self) -> None:
        # 95×8 → e1RM = 95 * (1 + 8/30) ≈ 120.33 — больше чем 105×3 (≈115.5)
        # и 100×5 (≈116.67). best_e1rm должен взять именно этот лог.
        rows = [
            (date(2026, 4, 6), 100.0, 5),
            (date(2026, 4, 7), 105.0, 3),
            (date(2026, 4, 8), 95.0, 8),
        ]
        weeks = build_exercise_progress(rows=rows)
        assert weeks[0].best_e1rm_kg == pytest.approx(120.33, abs=0.01)

    def test_sets_and_tonnage_sum_per_week(self) -> None:
        # Тоннаж = Σ(weight × reps). Сеты = COUNT(logs). Округление тоннажа
        # до 2 знаков, чтобы не плодить шум во фронте.
        rows = [
            (date(2026, 4, 6), 100.0, 5),  # 500
            (date(2026, 4, 8), 80.0, 8),   # 640
        ]
        weeks = build_exercise_progress(rows=rows)
        assert weeks[0].sets == 2
        assert weeks[0].tonnage_kg == pytest.approx(1140.0)

    def test_weeks_sorted_ascending_by_week_start(self) -> None:
        # Сервис может прислать в любом порядке (зависит от SQL); helper сам
        # сортирует, чтобы UI рисовал ось X без сюрпризов.
        rows = [
            (date(2026, 4, 20), 80.0, 5),
            (date(2026, 4, 6), 75.0, 5),
            (date(2026, 4, 13), 78.0, 5),
        ]
        weeks = build_exercise_progress(rows=rows)
        assert [w.week_start for w in weeks] == [
            date(2026, 4, 6),
            date(2026, 4, 13),
            date(2026, 4, 20),
        ]

    def test_returns_typed_dataclass(self) -> None:
        rows = [(date(2026, 4, 6), 100.0, 5)]
        weeks = build_exercise_progress(rows=rows)
        assert isinstance(weeks[0], ExerciseProgressWeek)
