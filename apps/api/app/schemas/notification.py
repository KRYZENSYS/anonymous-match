"""Notification, Premium, Admin sxemalari."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import Field

from app.schemas.auth import BaseSchema


class NotificationPublic(BaseSchema):
    id: int
    type: str
    title: str
    body: str
    icon: Optional[str] = None
    data: Optional[dict] = None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseSchema):
    notifications: List[NotificationPublic]
    unread_count: int
    total: int
    has_more: bool


class PremiumStatus(BaseSchema):
    is_premium: bool
    tier: str
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    days_left: int = 0
    auto_renew: bool = False
    super_likes_remaining: int
    likes_remaining: int
    boost_count: int = 0
    last_boost_at: Optional[datetime] = None


class PremiumPlan(BaseSchema):
    tier: Literal["plus", "gold", "platinum"]
    name: str
    duration_days: int
    price_stars: int
    price_usd: float
    features: List[str]


class PremiumPlansResponse(BaseSchema):
    plans: List[PremiumPlan]


class PurchaseRequest(BaseSchema):
    tier: Literal["plus", "gold", "platinum"]


class MediaUploadResponse(BaseSchema):
    id: int
    type: str
    url: str
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: Optional[int] = None
    duration_sec: Optional[int] = None


class BoostResponse(BaseSchema):
    success: bool
    boost_expires_at: Optional[datetime] = None
    remaining_boosts: int
    message: str


class AdminStats(BaseSchema):
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


class BanUserRequest(BaseSchema):
    user_id: int
    reason: str = Field(..., min_length=5, max_length=512)
    duration_days: Optional[int] = Field(None, ge=1, le=365)


class SuspendUserRequest(BaseSchema):
    user_id: int
    reason: str
    until: datetime


class BroadcastRequest(BaseSchema):
    title: str = Field(..., min_length=1, max_length=128)
    body: str = Field(..., min_length=1, max_length=1024)
    target: Literal["all", "premium", "online", "new_users"] = "all"
    image_url: Optional[str] = None
