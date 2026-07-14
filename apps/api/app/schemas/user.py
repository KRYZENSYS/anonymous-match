"""User va Profile sxemalari."""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import Field, field_validator

from app.schemas.auth import BaseSchema


class ProfileBase(BaseSchema):
    nickname: str = Field(..., min_length=2, max_length=32)
    bio: Optional[str] = Field(None, max_length=500)
    birth_date: date
    gender: Literal["male", "female", "other"]
    looking_for: Literal["male", "female", "everyone"] = "everyone"
    region: Optional[str] = Field(None, max_length=64)
    city: Optional[str] = Field(None, max_length=64)
    interests: List[str] = Field(default_factory=list, max_length=20)
    avatar_url: Optional[str] = None
    photos: List[str] = Field(default_factory=list, max_length=6)
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    occupation: Optional[str] = Field(None, max_length=64)
    education: Optional[str] = Field(None, max_length=64)
    languages: List[str] = Field(default_factory=lambda: ["uz"], max_length=10)
    min_age_preference: int = Field(18, ge=18, le=99)
    max_age_preference: int = Field(99, ge=18, le=99)
    max_distance_km: int = Field(100, ge=1, le=10000)
    show_only_online: bool = False
    show_only_in_region: bool = False

    @field_validator("nickname")
    @classmethod
    def nickname_clean(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nickname bush")
        if not all(c.isalnum() or c in "_- " for c in v):
            raise ValueError("Nickname faqat harflar va raqamlar")
        return v

    @field_validator("birth_date")
    @classmethod
    def age_check(cls, v: date) -> date:
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Yosh 18 dan kichik bolmasligi kerak")
        if age > 100:
            raise ValueError("Yosh 100 dan katta bolmasligi kerak")
        return v

    @field_validator("interests", "photos")
    @classmethod
    def sanitize_strings(cls, v: List[str]) -> List[str]:
        import bleach
        return [bleach.clean(s, strip=True)[:255] for s in v if s]


class ProfileUpdate(BaseSchema):
    nickname: Optional[str] = Field(None, min_length=2, max_length=32)
    bio: Optional[str] = Field(None, max_length=500)
    gender: Optional[Literal["male", "female", "other"]] = None
    looking_for: Optional[Literal["male", "female", "everyone"]] = None
    region: Optional[str] = Field(None, max_length=64)
    city: Optional[str] = Field(None, max_length=64)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    interests: Optional[List[str]] = Field(None, max_length=20)
    avatar_url: Optional[str] = None
    photos: Optional[List[str]] = Field(None, max_length=6)
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    occupation: Optional[str] = Field(None, max_length=64)
    education: Optional[str] = Field(None, max_length=64)
    languages: Optional[List[str]] = Field(None, max_length=10)
    min_age_preference: Optional[int] = Field(None, ge=18, le=99)
    max_age_preference: Optional[int] = Field(None, ge=18, le=99)
    max_distance_km: Optional[int] = Field(None, ge=1, le=10000)
    show_only_online: Optional[bool] = None
    show_only_in_region: Optional[bool] = None


class ProfilePublic(BaseSchema):
    public_id: str
    nickname: str
    age: Optional[int] = None
    gender: str
    looking_for: str
    region: Optional[str] = None
    city: Optional[str] = None
    interests: List[str] = []
    avatar_url: Optional[str] = None
    photos: List[str] = []
    height_cm: Optional[int] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    languages: List[str] = []
    bio: Optional[str] = None
    is_online: bool = False
    last_seen: Optional[datetime] = None
    is_verified: bool = False
    is_premium: bool = False
    is_boosted: bool = False
    distance_km: Optional[float] = None


class ProfileMe(ProfilePublic):
    user_id: int
    telegram_id: int
    telegram_first_name: Optional[str] = None
    telegram_photo_url: Optional[str] = None
    is_telegram_premium: bool = False
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


class DiscoverFilters(BaseSchema):
    min_age: int = Field(18, ge=18, le=99)
    max_age: int = Field(99, ge=18, le=99)
    gender: Optional[Literal["male", "female", "other", "any"]] = "any"
    region: Optional[str] = None
    city: Optional[str] = None
    max_distance_km: Optional[int] = Field(None, ge=1, le=10000)
    online_only: bool = False
    interests: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=50)


class BlockRequest(BaseSchema):
    blocked_id: int
    reason: Optional[str] = Field(None, max_length=255)


class ReportRequest(BaseSchema):
    reported_id: int
    reason: Literal["spam", "fake_profile", "inappropriate", "harassment", "scam", "underage", "hate_speech", "doxing", "other"]
    description: Optional[str] = Field(None, max_length=1000)
    chat_id: Optional[int] = None
    message_id: Optional[int] = None
    media_id: Optional[int] = None


class LocationUpdate(BaseSchema):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
