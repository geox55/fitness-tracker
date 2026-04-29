"""End-to-end auth flow через HTTP. Покрывает spec 001 в полном составе."""

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.domains.auth.models import AuthToken, User


@pytest.fixture
def verification_on() -> Iterator[None]:
    """Включаем проверку email на время теста. После — возвращаем дефолт.

    Settings закэширован lru_cache'ом, поэтому переменная окружения должна
    быть выставлена ДО clear() и сброшена ПОСЛЕ.
    """
    saved = os.environ.get("EMAIL_VERIFICATION_REQUIRED")
    os.environ["EMAIL_VERIFICATION_REQUIRED"] = "true"
    get_settings.cache_clear()
    yield
    if saved is None:
        os.environ.pop("EMAIL_VERIFICATION_REQUIRED", None)
    else:
        os.environ["EMAIL_VERIFICATION_REQUIRED"] = saved
    get_settings.cache_clear()


class TestRegisterAndVerify:
    pytestmark = pytest.mark.usefixtures("verification_on")

    async def test_register_creates_unconfirmed_user_and_token(
        self, client, db_session: AsyncSession
    ) -> None:
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "alice@example.com", "password": "password1"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email_status"] == "unconfirmed"

        # В БД появился user.
        users = (
            (await db_session.execute(select(User).where(User.email == "alice@example.com")))
            .scalars()
            .all()
        )
        assert len(users) == 1
        assert users[0].email_status == "unconfirmed"

        # Появился email_verify токен.
        tokens = (
            (
                await db_session.execute(
                    select(AuthToken).where(
                        AuthToken.user_id == users[0].id,
                        AuthToken.type == "email_verify",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(tokens) == 1

    async def test_login_blocked_for_unconfirmed(self, client) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={"email": "bob@example.com", "password": "password1"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "bob@example.com", "password": "password1"},
        )
        assert resp.status_code == 403
        assert resp.json()["detail"]["error"] == "email_unconfirmed"

    async def test_full_register_verify_login_flow(
        self, client, db_session: AsyncSession
    ) -> None:
        # 1. Регистрация
        await client.post(
            "/api/v1/auth/register",
            json={"email": "carol@example.com", "password": "password1"},
        )
        # Достаём raw-токен через служебный канал — в реальной жизни он
        # приходит email'ом, но в тесте email-sender — Logging, и БД хранит
        # только хэш. Поэтому вынимаем токен из логов невозможно — генерим
        # свой через resend-verification: он создаст ещё один token и сразу
        # отдадим его через подменённый sender. Проще: знаем алгоритм
        # _hash_token + ищем по нему. Но raw-токен сервер не отдаёт.
        # Вариант рабочий: подмена email-sender, которая сохранит token.
        # Делаем просто: достаём token из таблицы и руками проставляем
        # used_at=NULL (по факту он уже unused), но надо raw — а его нет.
        #
        # Решение: register-endpoint возвращает только user_id; для теста
        # пробрасываем dev-помощник: ищем токен в БД, генерим новый через
        # внутренний service.issue_one_time_token и используем его.
        from app.domains.auth.service import issue_one_time_token

        user = (
            (
                await db_session.execute(
                    select(User).where(User.email == "carol@example.com")
                )
            )
            .scalars()
            .one()
        )
        raw = await issue_one_time_token(
            db_session, user_id=user.id, kind="email_verify"
        )
        await db_session.commit()

        # 2. Verify
        verify_resp = await client.post(
            "/api/v1/auth/verify-email", json={"token": raw}
        )
        assert verify_resp.status_code == 204

        # 3. Login
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "carol@example.com", "password": "password1"},
        )
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        # 4. /profile/me с access-токеном
        me_resp = await client.get(
            "/api/v1/profile/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "carol@example.com"


class TestRefreshRotation:
    pytestmark = pytest.mark.usefixtures("verification_on")

    async def test_refresh_rotates_and_old_token_marked_used(
        self, client, db_session: AsyncSession
    ) -> None:
        from app.domains.auth.service import issue_one_time_token

        # Setup: подтверждённый юзер.
        await client.post(
            "/api/v1/auth/register",
            json={"email": "dan@example.com", "password": "password1"},
        )
        user = (
            await db_session.execute(
                select(User).where(User.email == "dan@example.com")
            )
        ).scalar_one()
        raw = await issue_one_time_token(
            db_session, user_id=user.id, kind="email_verify"
        )
        await db_session.commit()
        await client.post("/api/v1/auth/verify-email", json={"token": raw})

        login = (
            await client.post(
                "/api/v1/auth/login",
                json={"email": "dan@example.com", "password": "password1"},
            )
        ).json()
        old_refresh = login["refresh_token"]

        # Первый refresh — успех.
        resp1 = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert resp1.status_code == 200
        new_refresh = resp1.json()["refresh_token"]
        assert new_refresh != old_refresh

        # Второй refresh со СТАРЫМ refresh — кража, 401 reused.
        resp2 = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert resp2.status_code == 401
        assert resp2.json()["detail"]["error"] == "refresh_reused"

        # Все refresh-токены пользователя инвалидированы — даже новый.
        resp3 = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": new_refresh}
        )
        assert resp3.status_code == 401
        # new_refresh был помечен used при invalidate_all → reused, а не invalid.
        assert resp3.json()["detail"]["error"] == "refresh_reused"


class TestRateLimit:
    pytestmark = pytest.mark.usefixtures("verification_on")

    async def test_five_failed_logins_lock_account(
        self, client, db_session: AsyncSession
    ) -> None:
        from app.domains.auth.rate_limit import get_login_tracker
        from app.domains.auth.service import issue_one_time_token

        # Подтверждённый юзер.
        await client.post(
            "/api/v1/auth/register",
            json={"email": "eve@example.com", "password": "password1"},
        )
        user = (
            await db_session.execute(
                select(User).where(User.email == "eve@example.com")
            )
        ).scalar_one()
        raw = await issue_one_time_token(
            db_session, user_id=user.id, kind="email_verify"
        )
        await db_session.commit()
        await client.post("/api/v1/auth/verify-email", json={"token": raw})

        # Сбрасываем глобальный tracker, чтобы не зависеть от других тестов.
        get_login_tracker().__init__()  # type: ignore[misc]

        # 5 неудачных попыток.
        for _ in range(5):
            r = await client.post(
                "/api/v1/auth/login",
                json={"email": "eve@example.com", "password": "WRONG"},
            )
            assert r.status_code == 401

        # Шестая — заблокирована, даже с правильным паролем.
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "eve@example.com", "password": "password1"},
        )
        assert r.status_code == 429
        assert "Retry-After" in r.headers
        assert r.json()["detail"]["error"] == "rate_limited"
        assert r.json()["detail"]["retry_after"] > 0
