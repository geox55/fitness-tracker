from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PreferencesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    inbody_reminder: bool
    plan_update: bool
    weekly_summary: bool
    email_enabled: bool
    updated_at: datetime


class PreferencesUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inbody_reminder: bool | None = None
    plan_update: bool | None = None
    weekly_summary: bool | None = None
    email_enabled: bool | None = None


class InboxItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    payload: dict[str, Any]
    read_at: datetime | None
    created_at: datetime


class InboxResponse(BaseModel):
    items: list[InboxItem]
    unread_count: int
    total: int
