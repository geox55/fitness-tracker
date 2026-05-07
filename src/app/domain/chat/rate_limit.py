"""Rate-limiter чата — Edge case §10: 30 сообщений в час на пользователя.

Тот же подход, что в auth/rate_limit: in-memory sliding window + явная
передача `now` для тестов. Для продакшна с несколькими worker'ами вынесем
в Redis (drop-in: тот же интерфейс).
"""

from __future__ import annotations

import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Final

WINDOW: Final = timedelta(hours=1)
MAX_MESSAGES: Final = 30


class ChatRateLimiter:
    def __init__(self) -> None:
        self._timestamps: dict[uuid.UUID, deque[datetime]] = defaultdict(deque)

    def _purge_old(self, user_id: uuid.UUID, now: datetime) -> None:
        q = self._timestamps[user_id]
        threshold = now - WINDOW
        while q and q[0] < threshold:
            q.popleft()

    def is_allowed(self, user_id: uuid.UUID, now: datetime) -> bool:
        self._purge_old(user_id, now)
        return len(self._timestamps[user_id]) < MAX_MESSAGES

    def record(self, user_id: uuid.UUID, now: datetime) -> None:
        self._purge_old(user_id, now)
        self._timestamps[user_id].append(now)

    def remaining(self, user_id: uuid.UUID, now: datetime) -> int:
        self._purge_old(user_id, now)
        return max(0, MAX_MESSAGES - len(self._timestamps[user_id]))


_default_limiter = ChatRateLimiter()


def get_chat_limiter() -> ChatRateLimiter:
    return _default_limiter
