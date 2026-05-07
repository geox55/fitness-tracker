"""Тесты normalize_decimal — REQ-04 + Edge cases §10."""

import pytest

from app.domain.inbody_pdf.parser import normalize_decimal


class TestNormalizeDecimal:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("80.5", 80.5),
            ("80,5", 80.5),  # Edge §10: запятая → точка
            ("1 331", 1331.0),  # пробел внутри числа (artifact extract)
            ("ll9. 7", 119.7),  # OCR: 'l' → '1'
            ("133l", 1331.0),  # OCR: trailing 'l' → '1'
            ("1O0", 100.0),  # OCR: 'O' → '0'
            ("21. 6", 21.6),
            ("0.5", 0.5),
            ("-1.5", -1.5),
        ],
    )
    def test_valid_inputs(self, raw: str, expected: float) -> None:
        assert normalize_decimal(raw) == pytest.approx(expected)

    @pytest.mark.parametrize(
        "raw",
        ["", "   ", ".", "abc", None],
    )
    def test_invalid_returns_none(self, raw: str | None) -> None:
        assert normalize_decimal(raw) is None  # type: ignore[arg-type]
