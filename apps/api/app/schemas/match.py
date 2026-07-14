"""Match schemas."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

from app.schemas.user import ProfilePublic


class SwipeRequest(BaseModel):
    target_user_id: int
    action: Literal["like", "pass", "superlike"]


class SwipeResponse(BaseModel):
    success: bool
    is_match: bool
    match_id: Optional[int] = None
    chat_id: Optional[int] = None
    remaining_likes: int
    remaining_superlikes: int
    message: Optional[str] = None


class MatchPublic(BaseModel):
    id: int
    matched_at: datetime
    is_new: bool
    other_user: ProfilePublic
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    unread_count: int
    is_first_message: bool


class MatchListResponse(BaseModel):
    matches: list[MatchPublic]
    total: int


class LikeReceived(BaseModel):
    id: int
    from_user: ProfilePublic
    action: str
    created_at: datetime
    is_mutual: bool
