"""User schemas."""
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


GenderType = Literal["male", "female", "other"]
LookingFor = Literal["male", "female", "everyone"]


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=3, max_length=32)
    bio: Optional[str] = Field(None, max_length=500)
    birth_date: Optional[date] = None
    gender: Optional[GenderType] = None
    looking_for: Optional[LookingFor] = None
    region: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[list[str]] = None
    avatar_url: Optional[str] = None
    photos: Optional[list[str]] = None
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    occupation: Optional[str] = None
    education: Optional[str] = None
    languages: Optional[list[str]] = None
    min_age_preference: Optional[int] = Field(None, ge=18, le=99)
    max_age_preference: Optional[int] = Field(None, ge=18, le=99)
    max_distance_km: Optional[int] = Field(None, ge=1, le=10000)
    show_only_online: Optional[bool] = None
    show_only_in_region: Optional[bool] = None


class LocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ProfilePublic(BaseModel):
    public_id: str
    nickname: str
    age: int
    gender: str
    looking_for: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    interests: list[str] = []
    avatar_url: Optional[str] = None
    photos: list[str] = []
    height_cm: Optional[int] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    languages: list[str] = []
    bio: Optional[str] = None
    is_online: bool
    last_seen: Optional[datetime] = None
    is_verified: bool
    is_premium: bool
    is_boosted: bool
    distance_km: Optional[float] = None


class ProfileMe(ProfilePublic):
    user_id: int
    telegram_id: int
    telegram_first_name: Optional[str] = None
    telegram_photo_url: Optional[str] = None
    is_telegram_premium: bool
    min_age_preference: int
    max_age_preference: int
    max_distance_km: int
    show_only_online: bool
    show_only_in_region: bool
    profile_views: int
    likes_received: int
    likes_sent: int
    match_count: int
    is_banned: bool
    is_suspended: bool
    role: str
    preferred_language: str
    theme: str
    created_at: datetime
    updated_at: datetime


class DiscoverFilters(BaseModel):
    min_age: int = 18
    max_age: int = 99
    gender: str = "any"
    region: Optional[str] = None
    city: Optional[str] = None
    online_only: bool = False


class BlockRequest(BaseModel):
    blocked_id: int
    reason: Optional[str] = None


class ReportRequest(BaseModel):
    reported_id: int
    reason: Literal["spam", "fake_profile", "inappropriate", "harassment", "scam", "underage", "hate_speech", "doxing", "other"]
    description: Optional[str] = Field(None, max_length=1000)
    chat_id: Optional[int] = None
    message_id: Optional[int] = None
    media_id: Optional[int] = None
