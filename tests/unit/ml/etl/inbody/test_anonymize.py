"""Тесты анонимизации — REQ-17."""

from ml.etl.inbody.anonymize import anon_user_id, date_offset_days


class TestAnonUserId:
    def test_deterministic(self) -> None:
        a = anon_user_id("user-42", salt="s")
        b = anon_user_id("user-42", salt="s")
        assert a == b

    def test_salt_changes_output(self) -> None:
        assert anon_user_id("user-42", salt="x") != anon_user_id(
            "user-42", salt="y"
        )

    def test_different_users_different_ids(self) -> None:
        assert anon_user_id("u1", salt="s") != anon_user_id("u2", salt="s")

    def test_length_is_16_hex(self) -> None:
        result = anon_user_id("user-42", salt="s")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)


class TestDateOffset:
    def test_within_range(self) -> None:
        for raw in ["a", "b", "c", "user-very-long-identifier-1234567890"]:
            offset = date_offset_days(raw, salt="s")
            assert -365 <= offset <= 365

    def test_deterministic(self) -> None:
        assert date_offset_days("u", salt="s") == date_offset_days("u", salt="s")

    def test_distinct_users_likely_distinct_offsets(self) -> None:
        offsets = {date_offset_days(f"u{i}", salt="s") for i in range(50)}
        # Не все одинаковые — пусть будет хотя бы 30 разных значений из 50.
        assert len(offsets) >= 30
