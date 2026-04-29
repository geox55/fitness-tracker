"""Rate-limiter для логина (spec 001 REQ-06).

Политика: 5 неудачных попыток за 10 минут на email → блок на 15 минут.
Successful login сбрасывает счётчик.

ВАЖНО: in-memory backend. Работает на одном инстансе FastAPI; в production
с несколькими worker'ами нужно вынести в Redis (drop-in: тот же интерфейс,
другая реализация). Для MVP / диплома этого достаточно — uvicorn запускается
с одним worker'ом, мы это явно фиксируем в deploy.
"""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Final

WINDOW: Final = timedelta(minutes=10)
MAX_FAILURES: Final = 5
LOCKOUT: Final = timedelta(minutes=15)


class LoginAttemptTracker:
    """Окно неудачных попыток + lockout по ключу (lowercase email).

    Структура:
    - _failures[key] = deque[timestamps_of_failures] — обрезаем старше WINDOW.
    - _lockouts[key] = lockout_until — установлен при превышении лимита.

    Тестируется передачей now явно: позволяет проверить TTL без time.sleep.
    """

    def __init__(self) -> None:
        self._failures: dict[str, deque[datetime]] = defaultdict(deque)
        self._lockouts: dict[str, datetime] = {}

    def _purge_old(self, key: str, now: datetime) -> None:
        q = self._failures[key]
        threshold = now - WINDOW
        while q and q[0] < threshold:
            q.popleft()

    def is_locked(self, key: str, now: datetime) -> int | None:
        """Если заблокирован — секунды до разблокировки (≥1), иначе None."""
        until = self._lockouts.get(key)
        if until is None:
            return None
        if until <= now:
            del self._lockouts[key]
            self._failures.pop(key, None)
            return None
        return max(1, int((until - now).total_seconds()))

    def record_failure(self, key: str, now: datetime) -> None:
        """Зафиксировать неудачу. Если порог достигнут — выставить lockout."""
        if self.is_locked(key, now) is not None:
            return  # уже заблокирован, новые попытки счётчик не двигают
        self._purge_old(key, now)
        self._failures[key].append(now)
        if len(self._failures[key]) >= MAX_FAILURES:
            self._lockouts[key] = now + LOCKOUT

    def record_success(self, key: str, now: datetime) -> None:
        """Успешный вход сбрасывает счётчик и lockout (если каким-то путём
        пробился — например админ снял блок вручную)."""
        self._failures.pop(key, None)
        self._lockouts.pop(key, None)


_default_tracker = LoginAttemptTracker()


def get_login_tracker() -> LoginAttemptTracker:
    return _default_tracker
