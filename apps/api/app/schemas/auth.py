"""Pydantic sxemalar — API uchun input/output validatsiya."""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ===== Base =====
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# ===== Auth =====
class TelegramAuthRequest(BaseSchema):
    """Telegram WebApp orqali login."""
    init_data: str = Field(..., min_length=10, max_length=4096)
    device_id: Optional[str] = Field(None, max_length=64)
    webapp_version: Optional[str] = Field(None, max_length=16)


class AuthResponse(BaseSchema):
    """Login muvaffaqiyatli bo'lganda."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # sekundlarda
    user_id: int
    public_id: str
    is_new_user: bool
    is_profile_complete: bool
    needs_profile_setup: bool


class DeviceInfo(BaseSchema):
    device_id: str
    device_name: Optional[str] = None
    platform: Optional[str] = None
    last_used_at: datetime
    is_current: bool
