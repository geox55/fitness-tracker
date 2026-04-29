"""Unit-тесты login rate-limiter (spec 001 REQ-06).

Передаём now явно вместо datetime.now() — позволяет проверить TTL без
time.sleep и без mock'а времени.
"""

from datetime import UTC, datetime, timedelta

from app.domains.auth.rate_limit import (
    LOCKOUT,
    MAX_FAILURES,
    WINDOW,
    LoginAttemptTracker,
)

T0 = datetime(2026, 4, 28, 12, 0, tzinfo=UTC)


class TestPolicy:
    def test_constants_match_spec(self) -> None:
        # Spec 001 REQ-06: 5 неудач за 10 минут → блок на 15 минут.
        assert MAX_FAILURES == 5
        assert WINDOW.total_seconds() == 10 * 60
        assert LOCKOUT.total_seconds() == 15 * 60


class TestLockout:
    def test_unlocked_initially(self) -> None:
        t = LoginAttemptTracker()
        assert t.is_locked("a@b.c", T0) is None

    def test_n_minus_one_failures_does_not_lock(self) -> None:
        t = LoginAttemptTracker()
        for i in range(MAX_FAILURES - 1):
            t.record_failure("a@b.c", T0 + timedelta(seconds=i))
        assert t.is_locked("a@b.c", T0 + timedelta(seconds=10)) is None

    def test_n_failures_locks(self) -> None:
        t = LoginAttemptTracker()
        for i in range(MAX_FAILURES):
            t.record_failure("a@b.c", T0 + timedelta(seconds=i))
        assert t.is_locked("a@b.c", T0 + timedelta(seconds=10)) is not None

    def test_lockout_returns_seconds_remaining(self) -> None:
        t = LoginAttemptTracker()
        for _ in range(MAX_FAILURES):
            t.record_failure("a@b.c", T0)
        # Сразу после блокировки — осталось ~15 минут.
        retry = t.is_locked("a@b.c", T0 + timedelta(seconds=1))
        assert retry is not None
        assert 800 <= retry <= 900  # 15*60=900, чуть меньше из-за +1с

    def test_lockout_expires(self) -> None:
        t = LoginAttemptTracker()
        for _ in range(MAX_FAILURES):
            t.record_failure("a@b.c", T0)
        after_lockout = T0 + LOCKOUT + timedelta(seconds=1)
        assert t.is_locked("a@b.c", after_lockout) is None

    def test_failures_outside_window_dont_count(self) -> None:
        t = LoginAttemptTracker()
        # 4 старые неудачи (старше WINDOW) + 1 свежая → не лочит.
        for i in range(MAX_FAILURES - 1):
            t.record_failure("a@b.c", T0 + timedelta(seconds=i))
        much_later = T0 + WINDOW + timedelta(minutes=1)
        t.record_failure("a@b.c", much_later)
        assert t.is_locked("a@b.c", much_later) is None

    def test_record_failure_during_lockout_does_not_extend(self) -> None:
        # Атакующий не должен иметь возможность бесконечно продлевать lockout.
        t = LoginAttemptTracker()
        for _ in range(MAX_FAILURES):
            t.record_failure("a@b.c", T0)
        end_first = T0 + LOCKOUT
        t.record_failure("a@b.c", T0 + timedelta(minutes=10))
        # Lockout не сдвинулся.
        assert t.is_locked("a@b.c", end_first + timedelta(seconds=1)) is None


class TestSuccessReset:
    def test_success_clears_failure_history(self) -> None:
        t = LoginAttemptTracker()
        for _ in range(MAX_FAILURES - 1):
            t.record_failure("a@b.c", T0)
        t.record_success("a@b.c", T0)
        # После сброса 4 новых неудач недостаточно для блока.
        for _ in range(MAX_FAILURES - 1):
            t.record_failure("a@b.c", T0)
        assert t.is_locked("a@b.c", T0) is None

    def test_success_clears_active_lockout(self) -> None:
        t = LoginAttemptTracker()
        for _ in range(MAX_FAILURES):
            t.record_failure("a@b.c", T0)
        assert t.is_locked("a@b.c", T0) is not None
        t.record_success("a@b.c", T0)
        assert t.is_locked("a@b.c", T0) is None


class TestPerKeyIsolation:
    def test_different_keys_dont_interfere(self) -> None:
        t = LoginAttemptTracker()
        for _ in range(MAX_FAILURES):
            t.record_failure("a@b.c", T0)
        # Другой email не заблокирован.
        assert t.is_locked("c@d.e", T0) is None
