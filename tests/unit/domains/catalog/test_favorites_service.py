"""Unit-тесты чистой логики избранных — spec 014.

Сами CRUD-функции тонкие SQL-обёртки и проверяются интеграцией; здесь —
только sort_favorites_first и помощник `_new_custom_exercise_id`.
"""

import uuid

from app.domains.catalog.favorites_service import sort_favorites_first
from app.domains.catalog.models import Exercise
from app.domains.catalog.owned_service import _new_custom_exercise_id


def _exercise(name: str, id_: uuid.UUID | None = None) -> Exercise:
    return Exercise(
        id=id_ or uuid.uuid4(),
        exercise_id=name.lower(),
        exercise_name=name,
        exercise_name_ru=None,
        primary_muscle_group="chest",
        secondary_muscle_group=[],
        equipment=[],
        body_region="upper",
    )


class TestSortFavoritesFirst:
    def test_favorites_go_first_in_original_order(self) -> None:
        a, b, c, d = _exercise("A"), _exercise("B"), _exercise("C"), _exercise("D")
        favs = {b.id, d.id}
        result = sort_favorites_first([a, b, c, d], favs)
        # B и D — избранные, сохраняют исходный порядок относительно друг друга;
        # A и C — остальные, тоже в исходном порядке.
        assert [e.exercise_name for e in result] == ["B", "D", "A", "C"]

    def test_empty_favorites_keeps_order(self) -> None:
        items = [_exercise("A"), _exercise("B")]
        result = sort_favorites_first(items, set())
        assert result == items

    def test_all_favorites_keeps_order(self) -> None:
        a, b = _exercise("A"), _exercise("B")
        result = sort_favorites_first([a, b], {a.id, b.id})
        assert result == [a, b]

    def test_unknown_favorite_ids_ignored(self) -> None:
        # ID отсутствующего в списке упражнения не ломает сортировку.
        a = _exercise("A")
        result = sort_favorites_first([a], {uuid.uuid4()})
        assert result == [a]

    def test_empty_input(self) -> None:
        assert sort_favorites_first([], {uuid.uuid4()}) == []


class TestNewCustomExerciseId:
    def test_has_user_prefix(self) -> None:
        # Префикс `usr_` отделяет пользовательское от сидинга, где id —
        # короткий slug (например, "bench-press-1").
        assert _new_custom_exercise_id().startswith("usr_")

    def test_uniqueness_under_burst(self) -> None:
        # 1000 вызовов подряд не должны давать коллизий: 12 hex даёт 2^48
        # вариантов, день рождения-парадокс для 1000 ничтожен.
        ids = {_new_custom_exercise_id() for _ in range(1000)}
        assert len(ids) == 1000
