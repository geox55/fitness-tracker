"""Unit-тесты GDPR-экспорта: чистый _serialize (spec 002 NFR-03)."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from app.domains.profile.export import EXPORT_SCHEMA_VERSION, _serialize


class TestSerialize:
    def test_datetime_to_isoformat(self) -> None:
        dt = datetime(2026, 4, 28, 12, 0, tzinfo=UTC)
        assert _serialize(dt) == "2026-04-28T12:00:00+00:00"

    def test_date_to_isoformat(self) -> None:
        assert _serialize(date(2026, 4, 28)) == "2026-04-28"

    def test_decimal_to_float(self) -> None:
        assert _serialize(Decimal("78.4")) == 78.4

    def test_uuid_to_string(self) -> None:
        u = uuid.UUID("11111111-2222-3333-4444-555555555555")
        assert _serialize(u) == "11111111-2222-3333-4444-555555555555"

    def test_list_serialized_recursively(self) -> None:
        data = [Decimal("1.5"), date(2026, 1, 1), "raw"]
        assert _serialize(data) == [1.5, "2026-01-01", "raw"]

    def test_passthrough_for_primitives(self) -> None:
        assert _serialize(42) == 42
        assert _serialize("hello") == "hello"
        assert _serialize(None) is None
        assert _serialize(True) is True


class TestSchemaVersion:
    def test_version_is_present(self) -> None:
        # Стабильный контракт для клиентов GDPR-экспорта.
        assert EXPORT_SCHEMA_VERSION == "1"
