from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    # Имя — опциональное на регистрации, чтобы flow «email + password»
    # тоже работал. Если передано — сразу пишется в UserProfile.name,
    # пользователь не увидит пустое поле «Имя» при первом заходе в профиль.
    name: str | None = Field(default=None, min_length=1, max_length=50)

    @field_validator("password")
    @classmethod
    def _password_strength(cls, v: str) -> str:
        # spec 001 REQ-10: ≥8 символов, мин. 1 цифра и 1 буква.
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("password must contain at least one letter")
        return v


class RegisterResponse(BaseModel):
    user_id: UUID
    email_status: Literal["unconfirmed", "active"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int  # секунды до экспирации access-токена


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10, max_length=2048)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=10, max_length=2048)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=20, max_length=128)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def _password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("password must contain at least one letter")
        return v


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    email_status: Literal["unconfirmed", "active"]
    created_at: datetime
