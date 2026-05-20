"""Тесты extract_fields — Scenarios 1, 2, 3 + Edge cases."""

from pathlib import Path

import pytest

from app.domain.inbody_pdf.parser import extract_fields

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestExtractMetricSynthetic:
    """Чистый metric-PDF без OCR-шума (как от современных моделей).

    Калиброванный синтетический текст — как идеально извлекается из чистого
    InBody 770/970 PDF. Регрессия здесь ловит изменения regex'ов в первую
    очередь.
    """

    TEXT = """\
InBody 770 Body Composition Result Sheet
ID: 42  Height: 175 cm  Age: 30  Gender: Male  Date: 07.05.2026

Weight 80.5 kg
Skeletal Muscle Mass 38.2 kg
Body Fat Mass 13.4 kg
Total Body Water 49.5 %
Protein 13.2 kg
Minerals 4.6 kg
BMI (Body Mass Index) 26.3
PBF (%) 16.6
Visceral Fat Level 7
Basal Metabolic Rate 1750 kcal
Fat Free Mass 67.1 kg
"""

    def test_template_inbody_770(self) -> None:
        result = extract_fields(self.TEXT)
        assert result.template == "inbody_770"

    def test_units_metric(self) -> None:
        result = extract_fields(self.TEXT)
        assert result.units == "metric"

    def test_extracts_all_fields(self) -> None:
        result = extract_fields(self.TEXT)

        assert result.extracted["weight_kg"] == pytest.approx(80.5)
        assert result.extracted["height_cm"] == pytest.approx(175.0)
        assert result.extracted["body_fat_percent"] == pytest.approx(16.6)
        assert result.extracted["muscle_mass_kg"] == pytest.approx(38.2)
        assert result.extracted["body_water_percent"] == pytest.approx(49.5)
        assert result.extracted["protein_kg"] == pytest.approx(13.2)
        assert result.extracted["minerals_kg"] == pytest.approx(4.6)
        assert result.extracted["visceral_fat_level"] == 7
        assert result.extracted["bmr_kcal"] == 1750
        assert result.extracted["fat_free_mass_kg"] == pytest.approx(67.1)
        assert result.extracted["bmi"] == pytest.approx(26.3)
        assert result.extracted["sex"] == "male"

    def test_template_match_yields_high_confidence(self) -> None:
        result = extract_fields(self.TEXT)
        assert all(c == "high" for c in result.confidence.values())

    def test_no_missing_fields(self) -> None:
        result = extract_fields(self.TEXT)
        assert result.missing_fields == ()


class TestRussianLocalizedPdf:
    """Локализованный PDF от российского провайдера InBody — все labels
    на русском, ни одного латинского InBody-маркера. Фактический pdfplumber-
    извлечённый текст из реального файла (260427_inbody_result.pdf).
    Регрессия здесь ловит сломанные русские паттерны."""

    TEXT = """\
Имя Егор Пол М Возраст 24 Рост 170 см Дата 27.04.26
Вес Выше нормы Мышцы Норма Жир Выше нормы
82.2 кг 32.8 кг 29.1 %
История состава тела 27.04.26
Вес, кг 82,2
Мышцы, кг 32,8
Жир, % 29,1
Вес Выше нормы 82.2 кг Висцеральный жир 9
Мышцы 32.8 кг Индекс массы тела Выше нормы 28.4
Жир Выше нормы 29.1 % Безжировая масса 58.2 кг
Вода 42.5 л
Обмен веществ 1628
Белок 11.6 кг Суточная норма калорий 2413 ккал
Кости Выше нормы 4.09 кг
"""

    def test_recognized_as_inbody(self) -> None:
        from app.domain.inbody_pdf.parser import is_inbody
        assert is_inbody(self.TEXT)

    def test_extracts_core_fields(self) -> None:
        result = extract_fields(self.TEXT)
        assert result.extracted["weight_kg"] == pytest.approx(82.2)
        assert result.extracted["height_cm"] == pytest.approx(170.0)
        assert result.extracted["body_fat_percent"] == pytest.approx(29.1)
        assert result.extracted["muscle_mass_kg"] == pytest.approx(32.8)
        assert result.extracted["bmi"] == pytest.approx(28.4)
        assert result.extracted["visceral_fat_level"] == 9
        # BMR — именно «Обмен веществ» (1628), не «Суточная норма» (2413 — это TDEE).
        assert result.extracted["bmr_kcal"] == 1628
        assert result.extracted["fat_free_mass_kg"] == pytest.approx(58.2)
        assert result.extracted["protein_kg"] == pytest.approx(11.6)
        assert result.extracted["minerals_kg"] == pytest.approx(4.09)
        assert result.extracted["sex"] == "male"


class TestImperialAndComma:
    """Edge cases §10: запятая, lbs/in → конверсия в metric."""

    def test_imperial_units_converted(self) -> None:
        text = "InBody 270\nbody weight, 200 lbs.\nPercent Body Fat 18.0 %"

        result = extract_fields(text)

        assert result.units == "imperial"
        # 200 lbs · 0.4536 ≈ 90.72
        assert result.extracted["weight_kg"] == pytest.approx(90.72, abs=0.05)

    def test_comma_decimal_normalized(self) -> None:
        text = "InBody 770\nWeight 80,5 kg\nPBF (%) 16,6"

        result = extract_fields(text)

        assert result.extracted["weight_kg"] == pytest.approx(80.5)
        assert result.extracted["body_fat_percent"] == pytest.approx(16.6)


class TestPartialAndMissing:
    """Scenario 2 — отчёт с пропущенными опциональными полями."""

    def test_only_required_fields_present(self) -> None:
        text = "InBody 270\nWeight 70 kg\nPBF 22.0 %"

        result = extract_fields(text)

        assert result.extracted["weight_kg"] == pytest.approx(70.0)
        assert result.extracted["body_fat_percent"] == pytest.approx(22.0)
        # Эти поля не присутствовали в тексте — должны попасть в missing.
        for f in (
            "muscle_mass_kg",
            "body_water_percent",
            "visceral_fat_level",
            "bmr_kcal",
            "protein_kg",
            "minerals_kg",
        ):
            assert f in result.missing_fields


class TestNotInBody:
    """Scenario 4 — произвольный документ."""

    def test_random_text_no_template(self) -> None:
        text = "Электричество за апрель: 1234 кВт·ч"

        result = extract_fields(text)

        assert result.template is None
        assert result.extracted == {}


class TestRealNoisyFixture:
    """Сохранённое extracted-text от реального Brown InBody 520.

    Текст шумный (lbs вместо kg, OCR-артефакты `ll9.7`, `133l kcal`,
    `5ft06. 01 n.` — последнее это `5'6"`). Парсер должен достать минимум:
    weight, height, %fat, BMI, BMR, sex, FFM.
    """

    @pytest.fixture
    def text(self) -> str:
        return (FIXTURE_DIR / "brown_inbody520.txt").read_text()

    def test_recognises_as_inbody(self, text: str) -> None:
        result = extract_fields(text)
        assert result.template is not None  # generic минимум

    def test_extracts_weight_from_imperial_with_ocr_noise(self, text: str) -> None:
        result = extract_fields(text)
        # 119.7 lbs → 54.29 kg (на самом деле в БД будет 54.3 после round)
        assert result.extracted["weight_kg"] == pytest.approx(54.3, abs=0.1)

    def test_extracts_height_from_imperial(self, text: str) -> None:
        result = extract_fields(text)
        # 5'6" = 167.64 cm
        assert result.extracted["height_cm"] == pytest.approx(167.6, abs=0.5)

    def test_extracts_pbf_from_table_row(self, text: str) -> None:
        result = extract_fields(text)
        assert result.extracted["body_fat_percent"] == pytest.approx(18.1)

    def test_extracts_bmi(self, text: str) -> None:
        result = extract_fields(text)
        assert result.extracted["bmi"] == pytest.approx(19.3)

    def test_extracts_bmr_with_ocr_noise(self, text: str) -> None:
        result = extract_fields(text)
        # «133l kcal» (l = OCR-1) → 1331
        assert result.extracted["bmr_kcal"] == 1331

    def test_extracts_sex(self, text: str) -> None:
        result = extract_fields(text)
        assert result.extracted["sex"] == "female"
