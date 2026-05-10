"""Тесты чистой логики планирования импорта PDF — spec 013.

Покрывает:
- classify_status (ready / partial / failed)
- plan_import (включая override-статусы encrypted/scanned/not_inbody)
- merge_for_confirmation (overrides → payload, удаление None'ом)
- has_required_fields
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.inbody_pdf import (
    REQUIRED_FIELDS,
    ParsedInBody,
    classify_status,
    has_required_fields,
    merge_for_confirmation,
    plan_import,
)


def _parsed(extracted: dict[str, float | int | str]) -> ParsedInBody:
    """Минимальный ParsedInBody для unit-тестов классификации."""
    return ParsedInBody(
        template="inbody_770",
        units="metric",
        extracted=extracted,
        confidence={k: "high" for k in extracted},
        missing_fields=(),
    )


class TestClassifyStatus:
    def test_ready_when_both_required_present(self) -> None:
        p = _parsed({"weight_kg": 80.0, "body_fat_percent": 18.0})
        assert classify_status(p) == "ready"

    def test_partial_when_only_weight(self) -> None:
        p = _parsed({"weight_kg": 80.0})
        assert classify_status(p) == "partial"

    def test_partial_when_only_body_fat(self) -> None:
        p = _parsed({"body_fat_percent": 18.0})
        assert classify_status(p) == "partial"

    def test_partial_when_optional_only(self) -> None:
        # Скажем, парсер достал только bmi и height — этого мало, но что-то
        # есть, пользователь сможет докрутить вручную → partial.
        p = _parsed({"bmi": 25.0, "height_cm": 175.0})
        assert classify_status(p) == "partial"

    def test_failed_when_nothing_extracted(self) -> None:
        p = _parsed({})
        assert classify_status(p) == "failed"


class TestPlanImport:
    """Главная диспетчеризация: что делать дальше с конкретным файлом."""

    INBODY_TEXT = """\
InBody 770 Body Composition Result Sheet
Weight 80.5 kg
PBF (%) 16.6
"""

    def test_ready_path_persists_file(self) -> None:
        plan = plan_import(text=self.INBODY_TEXT, status_override=None)

        assert plan.status == "ready"
        assert plan.parsed is not None
        assert plan.persist_file is True

    def test_partial_path_persists_file(self) -> None:
        # Только weight — нужен оба обязательных, поэтому partial,
        # но файл всё равно сохраняем (юзер сможет дозаполнить на превью).
        text = "InBody 270\nWeight 70 kg\n"
        plan = plan_import(text=text, status_override=None)

        assert plan.status == "partial"
        assert plan.persist_file is True

    def test_not_inbody_does_not_persist(self) -> None:
        plan = plan_import(
            text="Электричество за апрель: 1234 кВт·ч",
            status_override=None,
        )

        assert plan.status == "not_inbody"
        assert plan.parsed is None
        assert plan.persist_file is False

    def test_encrypted_override_short_circuits_parser(self) -> None:
        # Текст пустой, но override уже всё решил — парсер не дёргаем.
        plan = plan_import(text="", status_override="encrypted")

        assert plan.status == "encrypted"
        assert plan.parsed is None
        assert plan.persist_file is False

    def test_scanned_override(self) -> None:
        plan = plan_import(text="", status_override="scanned_unsupported")

        assert plan.status == "scanned_unsupported"
        assert plan.persist_file is False

    def test_failed_override_when_pdfplumber_could_not_open(self) -> None:
        plan = plan_import(text="", status_override="failed")

        assert plan.status == "failed"
        assert plan.persist_file is False


class TestMergeForConfirmation:
    NOW = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)

    def test_extracted_only_used_when_no_overrides(self) -> None:
        payload = merge_for_confirmation(
            extracted={"weight_kg": 80.0, "body_fat_percent": 18.0},
            overrides=None,
            measured_at=self.NOW,
        )
        assert payload["weight_kg"] == 80.0
        assert payload["body_fat_percent"] == 18.0
        assert payload["measured_at"] == self.NOW

    def test_overrides_replace_extracted_values(self) -> None:
        payload = merge_for_confirmation(
            extracted={"weight_kg": 80.0, "body_fat_percent": 18.0},
            overrides={"weight_kg": 79.5},
            measured_at=self.NOW,
        )
        assert payload["weight_kg"] == 79.5
        assert payload["body_fat_percent"] == 18.0

    def test_overrides_can_add_missing_field(self) -> None:
        payload = merge_for_confirmation(
            extracted={"weight_kg": 80.0, "body_fat_percent": 18.0},
            overrides={"muscle_mass_kg": 35.0},
            measured_at=self.NOW,
        )
        assert payload["muscle_mass_kg"] == 35.0

    def test_overrides_none_clears_field(self) -> None:
        # Пользователь явно стёр некорректный visceral_fat на превью —
        # значение не попадает в БД.
        payload = merge_for_confirmation(
            extracted={
                "weight_kg": 80.0,
                "body_fat_percent": 18.0,
                "visceral_fat_level": 99,
            },
            overrides={"visceral_fat_level": None},
            measured_at=self.NOW,
        )
        assert "visceral_fat_level" not in payload

    def test_overrides_cannot_overwrite_measured_at(self) -> None:
        # `measured_at` ставится последним и не зависит от overrides —
        # дата приходит отдельным параметром.
        payload = merge_for_confirmation(
            extracted={"weight_kg": 80.0, "body_fat_percent": 18.0},
            overrides={"measured_at": "ignored"},
            measured_at=self.NOW,
        )
        assert payload["measured_at"] == self.NOW

    def test_does_not_mutate_input_extracted(self) -> None:
        extracted = {"weight_kg": 80.0, "body_fat_percent": 18.0}
        merge_for_confirmation(
            extracted=extracted,
            overrides={"weight_kg": 79.0},
            measured_at=self.NOW,
        )
        assert extracted == {"weight_kg": 80.0, "body_fat_percent": 18.0}


class TestHasRequiredFields:
    def test_all_present(self) -> None:
        assert has_required_fields(
            {"weight_kg": 80.0, "body_fat_percent": 18.0}
        )

    def test_missing_weight(self) -> None:
        assert not has_required_fields({"body_fat_percent": 18.0})

    def test_missing_body_fat(self) -> None:
        assert not has_required_fields({"weight_kg": 80.0})

    def test_none_value_treated_as_missing(self) -> None:
        # Если merge_for_confirmation удалил поле через override=None,
        # has_required_fields должен это поймать (а не пропустить).
        assert not has_required_fields(
            {"weight_kg": 80.0, "body_fat_percent": None}
        )

    def test_required_fields_match_module_constant(self) -> None:
        # Защита от рассинхрона: если кто-то изменит REQUIRED_FIELDS,
        # пусть тест явно подсветит — это конвенция.
        assert REQUIRED_FIELDS == ("weight_kg", "body_fat_percent")
