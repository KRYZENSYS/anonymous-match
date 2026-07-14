"""Notification schemas."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class NotificationPublic(BaseModel):
    id: int
    type: str
    title: str
    body: str
    icon: Optional[str] = None
    data: Optional[dict] = None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    notifications: list[NotificationPublic]
    unread_count: int
    total: int
    has_more: bool


# Premium
class PremiumStatus(BaseModel):
    is_premium: bool
    tier: str
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    days_left: int
    auto_renew: bool
    super_likes_remaining: int
    likes_remaining: int
    boost_count: int
    last_boost_at: Optional[datetime] = None


class PremiumPlan(BaseModel):
    tier: str
    name: str
    duration_days: int
    price_stars: int
    price_usd: float
    features: list[str]


class PremiumPlansResponse(BaseModel):
    plans: list[PremiumPlan]


class BoostResponse(BaseModel):
    success: bool
    boost_expires_at: Optional[datetime] = None
    remaining_boosts: int
    message: str


# Media
class MediaUploadResponse(BaseModel):
    id: int
    type: str
    url: str
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: int
    duration_sec: Optional[int] = None


# Admin
class AdminStats(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    new_users_today: int
    total_matches: int
    total_messages: int
    total_reports_pending: int
    total_premium_users: int
    revenue_total_stars: int
    online_now: int


class BanUserRequest(BaseModel):
    user_id: int
    reason: str
    duration_days: Optional[int] = None


class SuspendUserRequest(BaseModel):
    user_id: int
    reason: str
    until: datetime


class BroadcastRequest(BaseModel):
    title: str
    body: str
    target: Literal["all", "premium", "online", "new_users"] = "all"
    image_url: Optional[str] = None
