"""Unit-тесты refresh-rotation: чистая логика классификатора (spec 001).

Полный e2e-flow требует БД (auth_tokens хранится в Postgres). Здесь
проверяем критичную часть — порядок и приоритет проверок reused-vs-expired,
который определяет ответ при компрометации токена.
"""

import uuid
from datetime import UTC, datetime, timedelta

from app.domains.auth.models import AuthToken
from app.domains.auth.service import (
    _hash_token,
    classify_refresh_record,
    is_token_expired,
)


def _record(
    *,
    used_at: datetime | None = None,
    expires_in: timedelta = timedelta(days=7),
) -> AuthToken:
    return AuthToken(
        user_id=uuid.uuid4(),
        type="refresh",
        token_hash="x" * 64,
        expires_at=datetime.now(UTC) + expires_in,
        used_at=used_at,
    )


class TestClassifyRefreshRecord:
    def test_none_record_is_not_found(self) -> None:
        assert classify_refresh_record(None) == "not_found"

    def test_fresh_unused_record_is_valid(self) -> None:
        assert classify_refresh_record(_record()) == "valid"

    def test_used_record_is_reused(self) -> None:
        used = _record(used_at=datetime.now(UTC) - timedelta(minutes=5))
        assert classify_refresh_record(used) == "reused"

    def test_reused_takes_priority_over_expired(self) -> None:
        # Если токен И use'нут, И просрочен — отдаём reused.
        # Иначе атакующий с украденным просроченным токеном получил бы
        # более мягкий "expired" вместо тревоги "reused".
        compromised = _record(
            used_at=datetime.now(UTC) - timedelta(days=1),
            expires_in=timedelta(days=-1),
        )
        assert classify_refresh_record(compromised) == "reused"

    def test_expired_unused_record_is_expired(self) -> None:
        old = _record(expires_in=timedelta(seconds=-1))
        assert classify_refresh_record(old) == "expired"


class TestHashToken:
    def test_hash_is_deterministic(self) -> None:
        assert _hash_token("abc") == _hash_token("abc")

    def test_different_inputs_produce_different_hashes(self) -> None:
        assert _hash_token("abc") != _hash_token("abd")

    def test_hash_is_sha256_length(self) -> None:
        # 256 бит / 4 = 64 hex-символа.
        assert len(_hash_token("anything")) == 64


class TestIsTokenExpired:
    def test_future_expiry_is_not_expired(self) -> None:
        assert is_token_expired(_record(expires_in=timedelta(hours=1))) is False

    def test_past_expiry_is_expired(self) -> None:
        assert is_token_expired(_record(expires_in=timedelta(seconds=-1))) is True

    def test_naive_datetime_does_not_crash(self) -> None:
        # Защита от смешения tz-aware и naive datetime в БД (Postgres + asyncpg
        # иногда отдаёт naive объекты). Главное — не падает с TypeError.
        tok = _record()
        tok.expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)
        # Naive trated as UTC ⇒ +1ч от now ⇒ не истёк.
        assert is_token_expired(tok) is False
