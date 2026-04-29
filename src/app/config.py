from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения. Загружается из переменных окружения и .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Окружение / общие
    env: str = "production"
    api_v1_prefix: str = "/api/v1"

    # БД
    database_url: str = Field(
        ...,
        description=(
            "Async DSN, например postgresql+asyncpg://app:pass@postgres:5432/fitness"
        ),
    )

    # Безопасность
    jwt_secret: str = Field(..., description="HS256 ключ для подписи JWT")
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 60 * 15  # 15 минут
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 30  # 30 дней

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Подтверждение email при регистрации.
    # False — register сразу активирует аккаунт, login не проверяет статус,
    # письмо не отправляется. Удобно для dev/demo без работающего SMTP.
    # True — обычный flow по spec 001 (письмо + verify + активация).
    email_verification_required: bool = False

    # Email (см. src/app/email.py).
    # Если smtp_host пустой — используется LoggingEmailSender (письма в логи).
    smtp_host: str = ""
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    # Implicit TLS (порт 465). Для Gmail/AWS SES/Yandex используется STARTTLS,
    # включается отдельным флагом smtp_starttls.
    smtp_use_tls: bool = False
    smtp_starttls: bool = False
    email_from: str = "noreply@fitness-tracker.local"
    app_base_url: str = "http://localhost:8080"

    # S3-совместимый storage (см. src/app/storage.py).
    # Если s3_endpoint пустой — используется in-memory backend (для тестов).
    s3_endpoint: str = ""
    s3_public_base_url: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "fitness-uploads"
    s3_region: str = "us-east-1"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
