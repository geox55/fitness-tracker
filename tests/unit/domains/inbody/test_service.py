"""Unit-тесты сервиса InBody — чистые helpers без БД (spec 003)."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domains.inbody.service import (
    HeightUnknownError,
    SexUnknownError,
    build_measurement,
    compute_bmi,
)


class TestComputeBmi:
    def test_classic_normal_bmi(self) -> None:
        # 70 kg, 175 cm → BMI = 70 / 1.75^2 = 22.857... → 22.9
        assert compute_bmi(Decimal("70"), Decimal("175")) == Decimal("22.9")

    def test_rounding_half_up(self) -> None:
        # 64 kg / 1.6^2 = 25.0 ровно — без сюрпризов от ROUND_HALF_EVEN.
        assert compute_bmi(Decimal("64"), Decimal("160")) == Decimal("25.0")

    def test_height_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="height_cm"):
            compute_bmi(Decimal("70"), Decimal("0"))


class TestBuildMeasurement:
    def _payload(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "measured_at": datetime(2026, 4, 1, tzinfo=UTC),
            "weight_kg": 78.4,
            "body_fat_percent": 18.2,
        }
        base.update(overrides)
        return base

    def test_uses_profile_height_and_sex_when_payload_missing(self) -> None:
        m = build_measurement(
            user_id=uuid.uuid4(),
            payload=self._payload(),
            profile_height_cm=Decimal("180"),
            profile_sex="male",
        )
        assert m.height_cm == Decimal("180")
        assert m.sex == "male"
        # BMI = 78.4 / 1.8^2 ≈ 24.197 → 24.2
        assert m.bmi == Decimal("24.2")

    def test_payload_overrides_profile(self) -> None:
        m = build_measurement(
            user_id=uuid.uuid4(),
            payload=self._payload(height_cm=170, sex="female"),
            profile_height_cm=Decimal("180"),
            profile_sex="male",
        )
        assert m.height_cm == Decimal("170")
        assert m.sex == "female"

    def test_missing_height_raises(self) -> None:
        with pytest.raises(HeightUnknownError):
            build_measurement(
                user_id=uuid.uuid4(),
                payload=self._payload(),
                profile_height_cm=None,
                profile_sex="male",
            )

    def test_missing_sex_raises(self) -> None:
        with pytest.raises(SexUnknownError):
            build_measurement(
                user_id=uuid.uuid4(),
                payload=self._payload(),
                profile_height_cm=Decimal("180"),
                profile_sex=None,
            )

    def test_optional_fields_default_to_none(self) -> None:
        m = build_measurement(
            user_id=uuid.uuid4(),
            payload=self._payload(),
            profile_height_cm=Decimal("180"),
            profile_sex="male",
        )
        assert m.muscle_mass_kg is None
        assert m.body_water_percent is None
        assert m.protein_kg is None
        assert m.minerals_kg is None
        assert m.visceral_fat_level is None
        assert m.bmr_kcal is None
        assert m.fat_free_mass_kg is None
        assert m.original_pdf_key is None

    def test_full_payload_preserved(self) -> None:
        m = build_measurement(
            user_id=uuid.uuid4(),
            payload=self._payload(
                muscle_mass_kg=35.1,
                body_water_percent=56.0,
                protein_kg=12.3,
                minerals_kg=3.8,
                visceral_fat_level=7,
                bmr_kcal=1750,
                fat_free_mass_kg=64.0,
            ),
            profile_height_cm=Decimal("180"),
            profile_sex="male",
        )
        assert m.muscle_mass_kg == Decimal("35.1")
        assert m.body_water_percent == Decimal("56.0")
        assert m.protein_kg == Decimal("12.3")
        assert m.minerals_kg == Decimal("3.8")
        assert m.visceral_fat_level == 7
        assert m.bmr_kcal == 1750
        assert m.fat_free_mass_kg == Decimal("64.0")

    def test_default_source_is_manual(self) -> None:
        m = build_measurement(
            user_id=uuid.uuid4(),
            payload=self._payload(),
            profile_height_cm=Decimal("180"),
            profile_sex="male",
        )
        assert m.source == "manual"

    def test_pdf_source_can_be_set(self) -> None:
        m = build_measurement(
            user_id=uuid.uuid4(),
            payload=self._payload(original_pdf_key="inbody-pdf/temp/x.pdf"),
            profile_height_cm=Decimal("180"),
            profile_sex="male",
            source="pdf",
        )
        assert m.source == "pdf"
        # storage-key, а не URL: signed URL генерируется в API на лету
        # из этого ключа (NFR-04 spec 013).
        assert m.original_pdf_key == "inbody-pdf/temp/x.pdf"
