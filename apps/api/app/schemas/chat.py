"""Chat sxemalari."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import Field

from app.schemas.auth import BaseSchema


class ChatPublic(BaseSchema):
    id: int
    other_user_public_id: str
    other_user_nickname: str
    other_user_avatar: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    unread_count: int = 0
    is_archived: bool = False
    is_match: bool = False
    is_online: bool = False
    created_at: datetime


class ChatListResponse(BaseSchema):
    chats: List[ChatPublic]
    total: int
    has_more: bool


class MessageCreate(BaseSchema):
    type: Literal["text", "image", "video", "voice", "sticker", "gif"] = "text"
    content: Optional[str] = Field(None, max_length=4000)
    media_id: Optional[int] = None
    reply_to_id: Optional[int] = None
    extra: Optional[dict] = None


class MessageUpdate(BaseSchema):
    content: str = Field(..., min_length=1, max_length=4000)


class MessagePublic(BaseSchema):
    id: int
    chat_id: int
    sender_id: int
    sender_public_id: str
    type: str
    content: Optional[str] = None
    media: Optional[dict] = None
    reply_to: Optional[dict] = None
    is_edited: bool = False
    is_deleted: bool = False
    is_mine: bool = False
    read_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime


class MessageListResponse(BaseSchema):
    messages: List[MessagePublic]
    total: int
    has_more: bool
    next_cursor: Optional[datetime] = None


class WSTypingEvent(BaseSchema):
    type: Literal["typing"] = "typing"
    chat_id: int
    is_typing: bool


class WSReadEvent(BaseSchema):
    type: Literal["read"] = "read"
    chat_id: int
    message_ids: List[int]


class WSPresenceEvent(BaseSchema):
    type: Literal["presence"] = "presence"
    user_id: int
    is_online: bool


class WSEvent(BaseSchema):
    type: Literal["message", "typing", "read", "presence", "match", "notification", "error"]
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
