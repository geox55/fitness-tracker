"""Unit-тесты email-инфраструктуры (без реального SMTP)."""

from collections.abc import Iterator
from email.message import EmailMessage

import pytest

from app.config import Settings
from app.email import (
    LoggingEmailSender,
    SmtpEmailSender,
    _build_message,
    build_password_reset_link,
    build_verification_link,
    get_email_sender,
)


class TestLinks:
    def test_verification_link_has_token_query(self) -> None:
        link = build_verification_link(
            base_url="http://app.local", token="abc-123"
        )
        assert link == "http://app.local/auth/verify-email?token=abc-123"

    def test_reset_link_has_token_query(self) -> None:
        link = build_password_reset_link(
            base_url="http://app.local", token="abc-123"
        )
        assert link == "http://app.local/auth/reset-password?token=abc-123"

    def test_trailing_slash_in_base_url_is_normalized(self) -> None:
        link = build_verification_link(
            base_url="http://app.local/", token="x"
        )
        assert link == "http://app.local/auth/verify-email?token=x"

    def test_token_is_url_encoded(self) -> None:
        # Если в токене окажется символ + или =, он экранируется.
        link = build_verification_link(
            base_url="http://app.local", token="a+b=c"
        )
        assert "token=a%2Bb%3Dc" in link


class TestBuildMessage:
    def test_message_has_required_headers(self) -> None:
        msg = _build_message(
            sender="from@x.com",
            to="to@y.com",
            subject="Sub",
            text_body="text",
            html_body="<p>html</p>",
        )
        assert isinstance(msg, EmailMessage)
        assert msg["From"] == "from@x.com"
        assert msg["To"] == "to@y.com"
        assert msg["Subject"] == "Sub"

    def test_message_is_multipart_with_html_alternative(self) -> None:
        msg = _build_message(
            sender="f@x.com",
            to="t@y.com",
            subject="s",
            text_body="plain",
            html_body="<b>html</b>",
        )
        # plain — основной content; html — alternative.
        parts = list(msg.iter_parts())
        # add_alternative создаёт multipart/alternative — иterate по частям.
        types = {p.get_content_type() for p in parts}
        assert "text/html" in types


class TestFactory:
    @pytest.fixture(autouse=True)
    def _clear_email_cache(self) -> Iterator[None]:
        # get_email_sender() закэширован через lru_cache. Сбрасываем до и после
        # каждого теста, чтобы тесты не "наследовали" sender друг от друга.
        get_email_sender.cache_clear()
        yield
        get_email_sender.cache_clear()

    def test_empty_smtp_host_returns_logging_sender(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Патчим напрямую в модуле app.email, потому что get_settings
        # импортирован туда as-name (from .config import get_settings).
        from app import email as email_mod

        monkeypatch.setattr(
            email_mod,
            "get_settings",
            lambda: Settings(  # type: ignore[call-arg]
                database_url="postgresql+asyncpg://x:y@z/db",
                jwt_secret="x" * 32,
                smtp_host="",
            ),
        )
        get_email_sender.cache_clear()
        assert isinstance(get_email_sender(), LoggingEmailSender)

    def test_nonempty_smtp_host_returns_smtp_sender(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app import email as email_mod

        monkeypatch.setattr(
            email_mod,
            "get_settings",
            lambda: Settings(  # type: ignore[call-arg]
                database_url="postgresql+asyncpg://x:y@z/db",
                jwt_secret="x" * 32,
                smtp_host="mailpit",
                smtp_port=1025,
            ),
        )
        get_email_sender.cache_clear()
        sender = get_email_sender()
        assert isinstance(sender, SmtpEmailSender)
