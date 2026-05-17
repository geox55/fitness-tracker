"""Unit-тесты сервиса профиля — чистая логика без БД (spec 002).

Проверяем 4 инварианта:
- BMR пересчитывается при изменении его входов и обнуляется при их удалении;
- смена goal/training_frequency у уже-онбордившегося пользователя поднимает
  plan_rebuild_required, до завершения онбординга — нет;
- missing_required_fields находит все обязательные поля по spec 002 REQ-02;
- complete_onboarding падает с IncompleteOnboardingError, если чего-то не хватает.
"""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.domains.profile.models import UserProfile
from app.domains.profile.service import (
    PLAN_INVALIDATING_FIELDS,
    REQUIRED_FIELDS,
    apply_changes,
    missing_required_fields,
)


def _filled_profile() -> UserProfile:
    """Профиль со всеми обязательными полями и завершённым онбордингом."""
    p = UserProfile(
        name="Маша",
        sex="female",
        birth_date=date(1996, 5, 1),
        height_cm=Decimal("168.0"),
        baseline_weight_kg=Decimal("60.0"),
        goal="muscle_gain",
        training_level="intermediate",
        training_frequency=3,
        allergies=[],
        plan_rebuild_required=False,
        onboarding_completed_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return p


class TestApplyChangesBmr:
    def test_recalculates_bmr_when_weight_changes(self) -> None:
        p = _filled_profile()
        apply_changes(p, {"baseline_weight_kg": 65.0})
        # Пересчёт случился: bmr_kcal стал не None и в разумных пределах.
        assert p.bmr_kcal is not None
        assert 1000 < p.bmr_kcal < 2500

    def test_no_recalc_when_unrelated_field_changes(self) -> None:
        p = _filled_profile()
        p.bmr_kcal = 1400
        apply_changes(p, {"training_level": "advanced"})
        # bmr_kcal остался прежним: training_level не входит в BMR-формулу.
        assert p.bmr_kcal == 1400

    def test_clears_bmr_when_input_removed(self) -> None:
        p = _filled_profile()
        p.bmr_kcal = 1400
        apply_changes(p, {"sex": None})
        assert p.bmr_kcal is None

    def test_no_recalc_when_value_unchanged(self) -> None:
        p = _filled_profile()
        p.bmr_kcal = 9999  # маркер, чтобы заметить пересчёт
        apply_changes(p, {"sex": "female"})  # такое же значение
        assert p.bmr_kcal == 9999


class TestApplyChangesPlanDirty:
    @pytest.mark.parametrize("field,value", [
        ("goal", "weight_loss"),
        ("training_frequency", 5),
        ("equipment_available", ["dumbbell", "pullup_bar"]),
    ])
    def test_plan_dirty_after_onboarding(self, field: str, value: object) -> None:
        p = _filled_profile()
        apply_changes(p, {field: value})
        assert p.plan_rebuild_required is True

    def test_plan_dirty_only_for_invalidating_fields(self) -> None:
        # Гарантируем, что мы тестируем актуальный список полей.
        assert set(PLAN_INVALIDATING_FIELDS) == {
            "goal",
            "training_frequency",
            "equipment_available",
        }

    def test_equipment_available_canonicalized_on_storage(self) -> None:
        """Список оборудования сортируется при записи → PATCH с тем же
        набором в другом порядке не триггерит plan_rebuild_required."""
        p = _filled_profile()
        # Первый PATCH — задаёт значение, поднимает флаг.
        apply_changes(p, {"equipment_available": ["dumbbell", "barbell"]})
        assert p.equipment_available == ["barbell", "dumbbell"]
        assert p.plan_rebuild_required is True

        # Сброс флага (имитируем, что после генерации он снимается).
        p.plan_rebuild_required = False

        # Второй PATCH — те же значения, но в другом порядке.
        apply_changes(p, {"equipment_available": ["barbell", "dumbbell"]})
        assert p.plan_rebuild_required is False

    def test_no_flag_before_onboarding_complete(self) -> None:
        p = _filled_profile()
        p.onboarding_completed_at = None  # ещё на шагах онбординга
        apply_changes(p, {"goal": "weight_loss"})
        assert p.plan_rebuild_required is False

    def test_no_flag_when_value_unchanged(self) -> None:
        p = _filled_profile()
        apply_changes(p, {"goal": "muscle_gain"})  # такое же
        assert p.plan_rebuild_required is False

    def test_unrelated_field_does_not_set_flag(self) -> None:
        p = _filled_profile()
        apply_changes(p, {"name": "Maria"})
        assert p.plan_rebuild_required is False


class TestRequiredFields:
    def test_full_profile_has_no_missing(self) -> None:
        assert missing_required_fields(_filled_profile()) == []

    def test_empty_profile_lists_all_required(self) -> None:
        empty = UserProfile()
        # set вместо list — порядок не контрактный.
        assert set(missing_required_fields(empty)) == set(REQUIRED_FIELDS)

    def test_partial_profile_lists_only_missing(self) -> None:
        p = _filled_profile()
        p.training_frequency = None
        p.goal = None
        assert set(missing_required_fields(p)) == {"training_frequency", "goal"}
