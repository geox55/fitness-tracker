"""Unit-тесты сервиса уведомлений (spec 011) — чистые helpers без БД."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domains.notifications.models import (
    USER_CONTROLLED_TYPES,
    NotificationPreferences,
)
from app.domains.notifications.service import (
    INBODY_REMINDER_AFTER_DAYS,
    INBODY_REMINDER_DEBOUNCE_DAYS,
    _inbody_reminder_due,
    should_send,
)

NOW = datetime(2026, 4, 28, 12, 0, tzinfo=UTC)


class TestShouldSendAuthTypes:
    @pytest.mark.parametrize("kind", ["email_verify", "password_reset"])
    def test_auth_types_always_send_regardless_of_prefs(self, kind: str) -> None:
        # spec 011 REQ-08: transactional auth-типы не управляются юзером.
        prefs = NotificationPreferences(
            inbody_reminder=False,
            plan_update=False,
            weekly_summary=False,
            email_enabled=False,
        )
        assert should_send(prefs=prefs, kind=kind, channel="email") is True
        assert should_send(prefs=prefs, kind=kind, channel="in_app") is True

    def test_auth_types_send_even_without_prefs_row(self) -> None:
        # Свежезарегистрированный юзер ещё не имеет preferences.
        assert (
            should_send(prefs=None, kind="email_verify", channel="email")
            is True
        )


class TestShouldSendUserControlled:
    @pytest.mark.parametrize("kind", sorted(USER_CONTROLLED_TYPES))
    def test_disabled_type_blocks_send(self, kind: str) -> None:
        prefs = NotificationPreferences(
            inbody_reminder=False,
            plan_update=False,
            weekly_summary=False,
            email_enabled=True,
        )
        assert should_send(prefs=prefs, kind=kind, channel="email") is False

    def test_email_disabled_blocks_email_only(self) -> None:
        # Тип включён, но глобально email выключен → in_app проходит, email нет.
        prefs = NotificationPreferences(
            inbody_reminder=True,
            plan_update=True,
            weekly_summary=True,
            email_enabled=False,
        )
        assert (
            should_send(prefs=prefs, kind="inbody_reminder", channel="email")
            is False
        )
        assert (
            should_send(prefs=prefs, kind="inbody_reminder", channel="in_app")
            is True
        )

    def test_no_prefs_row_uses_defaults_true(self) -> None:
        # Дефолты в модели — все True (REQ-06).
        assert (
            should_send(prefs=None, kind="inbody_reminder", channel="email")
            is True
        )


class TestInbodyReminderDue:
    def test_constants_match_spec(self) -> None:
        # spec 011 REQ-05: триггер >30 дней; debounce 7 дней.
        assert INBODY_REMINDER_AFTER_DAYS == 30
        assert INBODY_REMINDER_DEBOUNCE_DAYS == 7

    def test_no_measurements_is_due(self) -> None:
        assert _inbody_reminder_due(last_measured_at=None, now=NOW) is True

    def test_recent_measurement_not_due(self) -> None:
        recent = NOW - timedelta(days=5)
        assert _inbody_reminder_due(last_measured_at=recent, now=NOW) is False

    def test_29_days_not_due(self) -> None:
        # Граница: ровно ДО 30 дней — ещё не пора.
        almost = NOW - timedelta(days=29, hours=23)
        assert _inbody_reminder_due(last_measured_at=almost, now=NOW) is False

    def test_30_days_is_due(self) -> None:
        # Граница: ровно 30 дней — уже пора (>=).
        boundary = NOW - timedelta(days=30)
        assert _inbody_reminder_due(last_measured_at=boundary, now=NOW) is True

    def test_old_measurement_due(self) -> None:
        old = NOW - timedelta(days=90)
        assert _inbody_reminder_due(last_measured_at=old, now=NOW) is True
