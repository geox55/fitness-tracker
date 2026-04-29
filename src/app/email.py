"""Email-отправка: интерфейс + dev/prod-реализации.

LoggingEmailSender — fallback, пишет токен в лог. Включается, когда не задан
`SMTP_HOST` (например, в unit-тестах, в локальной разработке без MailPit).

SmtpEmailSender — для dev (MailPit на 1025) и prod (внешний SMTP-сервис).
Письма plain-text + multipart с HTML-частью; Jinja намеренно не тащим, чтобы
не плодить зависимости — шаблонов всего два, форматирование .format() хватает.

Выбор реализации — по `Settings.smtp_host`. Если хост пустой — Logging,
иначе SMTP. Это позволяет одной env-переменной переключить sender без правок
бизнес-кода (см. spec 011 REQ-01).
"""

from __future__ import annotations

import logging
from email.message import EmailMessage
from functools import lru_cache
from typing import Protocol
from urllib.parse import urlencode

import aiosmtplib

from .config import Settings, get_settings

_log = logging.getLogger("app.email")


class EmailSender(Protocol):
    async def send_email_verification(self, *, to: str, token: str) -> None: ...
    async def send_password_reset(self, *, to: str, token: str) -> None: ...


# ---- Dev fallback: пишем в лог -------------------------------------------


class LoggingEmailSender:
    async def send_email_verification(self, *, to: str, token: str) -> None:
        _log.info("[email-verify] to=%s token=%s", to, token)

    async def send_password_reset(self, *, to: str, token: str) -> None:
        _log.info("[password-reset] to=%s token=%s", to, token)


# ---- Реальная отправка через SMTP ----------------------------------------


_VERIFY_SUBJECT = "Подтвердите email — Fitness Tracker"
_RESET_SUBJECT = "Сброс пароля — Fitness Tracker"

_VERIFY_TEXT = (
    "Здравствуйте!\n\n"
    "Вы зарегистрировались в Fitness Tracker. Перейдите по ссылке, чтобы "
    "подтвердить email и активировать аккаунт:\n\n"
    "{link}\n\n"
    "Ссылка действительна 24 часа. Если вы не регистрировались — просто "
    "проигнорируйте письмо.\n"
)

_VERIFY_HTML = (
    "<p>Здравствуйте!</p>"
    "<p>Вы зарегистрировались в Fitness Tracker. "
    "Нажмите кнопку, чтобы подтвердить email:</p>"
    '<p><a href="{link}" style="background:#1f6feb;color:#fff;padding:12px 20px;'
    'text-decoration:none;border-radius:6px;display:inline-block">'
    "Подтвердить email</a></p>"
    "<p>Если кнопка не работает, скопируйте ссылку:<br>"
    '<a href="{link}">{link}</a></p>'
    "<p>Ссылка действительна 24 часа. Если вы не регистрировались — "
    "просто проигнорируйте письмо.</p>"
)

_RESET_TEXT = (
    "Здравствуйте!\n\n"
    "Вы запросили сброс пароля. Перейдите по ссылке:\n\n"
    "{link}\n\n"
    "Ссылка действительна 1 час. Если запрос отправили не вы — "
    "проигнорируйте письмо.\n"
)

_RESET_HTML = (
    "<p>Здравствуйте!</p>"
    "<p>Вы запросили сброс пароля. Нажмите кнопку:</p>"
    '<p><a href="{link}" style="background:#1f6feb;color:#fff;padding:12px 20px;'
    'text-decoration:none;border-radius:6px;display:inline-block">'
    "Сбросить пароль</a></p>"
    "<p>Или скопируйте ссылку:<br>"
    '<a href="{link}">{link}</a></p>'
    "<p>Ссылка действительна 1 час. Если запрос отправили не вы — "
    "проигнорируйте письмо.</p>"
)


def build_verification_link(*, base_url: str, token: str) -> str:
    """Deep-link, который PWA должна обработать на клиенте: достать `token`
    из query и дёрнуть POST /auth/verify-email."""
    return f"{base_url.rstrip('/')}/auth/verify-email?{urlencode({'token': token})}"


def build_password_reset_link(*, base_url: str, token: str) -> str:
    return f"{base_url.rstrip('/')}/auth/reset-password?{urlencode({'token': token})}"


def _build_message(
    *, sender: str, to: str, subject: str, text_body: str, html_body: str
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    return msg


class SmtpEmailSender:
    """Отправка через aiosmtplib. Production / dev (MailPit) одинаково.

    Параметры берём из Settings один раз — sender stateless.
    """

    def __init__(self, settings: Settings) -> None:
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_username or None
        self._password = settings.smtp_password or None
        self._use_tls = settings.smtp_use_tls
        self._starttls = settings.smtp_starttls
        self._from = settings.email_from
        self._base_url = settings.app_base_url

    async def _send(self, msg: EmailMessage) -> None:
        # Три режима TLS у aiosmtplib:
        # - use_tls=True            — implicit TLS (порт 465, AWS SES/Yandex465)
        # - start_tls=True          — STARTTLS (порт 587, Gmail/SES/SMTP relay)
        # - оба False               — plaintext (MailPit, локальный dev)
        try:
            await aiosmtplib.send(
                msg,
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                use_tls=self._use_tls,
                start_tls=self._starttls,
            )
        except aiosmtplib.SMTPException:
            # Не валим бизнес-flow из-за SMTP-проблем: token уже сохранён в БД,
            # пользователь сможет нажать "отправить повторно".
            _log.exception("SMTP send failed to=%s subject=%s", msg["To"], msg["Subject"])

    async def send_email_verification(self, *, to: str, token: str) -> None:
        link = build_verification_link(base_url=self._base_url, token=token)
        msg = _build_message(
            sender=self._from,
            to=to,
            subject=_VERIFY_SUBJECT,
            text_body=_VERIFY_TEXT.format(link=link),
            html_body=_VERIFY_HTML.format(link=link),
        )
        await self._send(msg)

    async def send_password_reset(self, *, to: str, token: str) -> None:
        link = build_password_reset_link(base_url=self._base_url, token=token)
        msg = _build_message(
            sender=self._from,
            to=to,
            subject=_RESET_SUBJECT,
            text_body=_RESET_TEXT.format(link=link),
            html_body=_RESET_HTML.format(link=link),
        )
        await self._send(msg)


# ---- Factory --------------------------------------------------------------


@lru_cache(maxsize=1)
def get_email_sender() -> EmailSender:
    settings = get_settings()
    if not settings.smtp_host:
        return LoggingEmailSender()
    return SmtpEmailSender(settings)
