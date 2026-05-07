"""Тесты detect_template + is_inbody — REQ-02 + Scenario 4."""

from app.domain.inbody_pdf.parser import detect_template, is_inbody


class TestIsInBody:
    def test_marker_detected(self) -> None:
        assert is_inbody("Some intro\nInBody 770 Body Composition Result\nFields...")

    def test_ocr_marker_detected(self) -> None:
        # 'lnBody' (lowercase L) — типичный OCR-артефакт.
        assert is_inbody("lnBody520 Direct Segmental BIA")

    def test_pbf_marker_alone_is_enough(self) -> None:
        assert is_inbody("Result\nWeight 80 kg\nPBF 18.0%")

    def test_unrelated_doc_not_inbody(self) -> None:
        assert not is_inbody("Счёт за электричество №42")


class TestDetectTemplate:
    def test_inbody_770(self) -> None:
        assert detect_template("Body Composition\nInBody 770 result") == "inbody_770"

    def test_inbody_270(self) -> None:
        assert detect_template("InBody 270 sample report\nWeight 80 kg") == "inbody_270"

    def test_inbody_970_with_ocr_l(self) -> None:
        assert detect_template("lnBody 970 Composition") == "inbody_970"

    def test_unknown_inbody_falls_to_generic(self) -> None:
        assert detect_template("InBody 520 results\nPBF 18%") == "generic"

    def test_non_inbody_returns_none(self) -> None:
        assert detect_template("Just a regular receipt") is None
