"""Unit-тесты одноразовых токенов и email-sender (spec 001 REQ-03/04)."""

import pytest

from app.domains.auth.service import (
    EMAIL_VERIFY_TTL,
    PASSWORD_RESET_TTL,
    _generate_one_time_token,
    _hash_token,
)
from app.email import LoggingEmailSender, get_email_sender


class TestTokenGeneration:
    def test_token_is_url_safe(self) -> None:
        # secrets.token_urlsafe → только [A-Za-z0-9_-].
        tok = _generate_one_time_token()
        allowed = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        )
        assert set(tok) <= allowed

    def test_each_token_unique(self) -> None:
        # 1000 генераций — коллизий не должно быть; вероятность <2^-200.
        tokens = {_generate_one_time_token() for _ in range(1000)}
        assert len(tokens) == 1000

    def test_token_length_is_anti_bruteforce(self) -> None:
        # token_urlsafe(32) → ≥43 символа base64url. Это даёт ≥256 бит энтропии.
        assert len(_generate_one_time_token()) >= 43

    def test_hash_does_not_leak_raw(self) -> None:
        raw = _generate_one_time_token()
        h = _hash_token(raw)
        assert raw not in h


class TestTtl:
    def test_email_verify_ttl_24h(self) -> None:
        # spec 001 REQ-03: TTL 24 часа.
        assert EMAIL_VERIFY_TTL.total_seconds() == 24 * 3600

    def test_password_reset_ttl_1h(self) -> None:
        # spec 001 REQ-04: TTL 1 час.
        assert PASSWORD_RESET_TTL.total_seconds() == 3600


class TestLoggingEmailSender:
    """LoggingEmailSender — dev-fallback. Точное содержимое лога ловить
    кросс-loop-scope в pytest хрупко (caplog теряет records в session-scoped
    event loop). Здесь проверяем только что вызов завершается без ошибок —
    сам факт логирования покрыт визуально через MailPit и интеграционным
    тестом регистрации."""

    @pytest.mark.asyncio
    async def test_verification_send_does_not_raise(self) -> None:
        await LoggingEmailSender().send_email_verification(
            to="x@example.com", token="abc123"
        )

    @pytest.mark.asyncio
    async def test_reset_send_does_not_raise(self) -> None:
        await LoggingEmailSender().send_password_reset(
            to="y@example.com", token="reset-tok"
        )


class TestEmailSenderFactory:
    def test_default_returns_logging_sender(self) -> None:
        # При smtp_host="" (дефолт в Settings) возвращается LoggingEmailSender.
        # Прод-SMTP активируется заданием SMTP_HOST в env.
        get_email_sender.cache_clear()
        assert isinstance(get_email_sender(), LoggingEmailSender)
