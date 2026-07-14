"""Match, Like, Swipe sxemalari."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import Field

from app.schemas.auth import BaseSchema
from app.schemas.user import ProfilePublic


class SwipeRequest(BaseSchema):
    target_user_id: int
    action: Literal["like", "superlike", "pass"]


class SwipeResponse(BaseSchema):
    success: bool
    is_match: bool = False
    match_id: Optional[int] = None
    chat_id: Optional[int] = None
    remaining_likes: int
    remaining_superlikes: int
    message: Optional[str] = None


class MatchPublic(BaseSchema):
    id: int
    matched_at: datetime
    is_new: bool
    other_user: ProfilePublic
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    unread_count: int = 0
    is_first_message: bool = True


class MatchListResponse(BaseSchema):
    matches: List[MatchPublic]
    total: int


class LikeReceived(BaseSchema):
    from_user: ProfilePublic
    is_super_like: bool
    is_mutual: bool
    created_at: datetime
