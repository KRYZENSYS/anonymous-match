"""Auth schemas."""
from pydantic import BaseModel, Field


class TelegramAuthRequest(BaseModel):
    init_data: str = Field(..., description="Telegram WebApp initData")
    device_id: str | None = None
    webapp_version: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user_id: int
    public_id: str
    is_new_user: bool
    is_profile_complete: bool
    needs_profile_setup: bool


class LogoutResponse(BaseModel):
    success: bool
    message: str
