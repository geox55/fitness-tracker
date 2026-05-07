"""Тесты rate-limiter'а чата — Edge case §10 (30 сообщений/час)."""

import uuid
from datetime import UTC, datetime, timedelta

from app.domain.chat.rate_limit import MAX_MESSAGES, ChatRateLimiter


class TestChatRateLimiter:
    def test_allows_first_messages(self) -> None:
        limiter = ChatRateLimiter()
        user = uuid.uuid4()
        now = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)

        for i in range(5):
            assert limiter.is_allowed(user, now)
            limiter.record(user, now + timedelta(seconds=i))

    def test_blocks_after_limit_exceeded(self) -> None:
        limiter = ChatRateLimiter()
        user = uuid.uuid4()
        now = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)

        for i in range(MAX_MESSAGES):
            assert limiter.is_allowed(user, now + timedelta(seconds=i))
            limiter.record(user, now + timedelta(seconds=i))

        assert not limiter.is_allowed(user, now + timedelta(seconds=MAX_MESSAGES))

    def test_old_messages_drop_out_of_window(self) -> None:
        limiter = ChatRateLimiter()
        user = uuid.uuid4()
        start = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)

        for i in range(MAX_MESSAGES):
            limiter.record(user, start + timedelta(seconds=i))

        # Через 61 минуту окно должно полностью смениться — снова можно слать.
        later = start + timedelta(minutes=61)
        assert limiter.is_allowed(user, later)

    def test_per_user_isolation(self) -> None:
        limiter = ChatRateLimiter()
        a = uuid.uuid4()
        b = uuid.uuid4()
        now = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)

        for i in range(MAX_MESSAGES):
            limiter.record(a, now + timedelta(seconds=i))

        assert not limiter.is_allowed(a, now + timedelta(minutes=1))
        # Другой пользователь не задет.
        assert limiter.is_allowed(b, now + timedelta(minutes=1))

    def test_remaining_decreases(self) -> None:
        limiter = ChatRateLimiter()
        user = uuid.uuid4()
        now = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)

        assert limiter.remaining(user, now) == MAX_MESSAGES
        limiter.record(user, now)
        assert limiter.remaining(user, now) == MAX_MESSAGES - 1
