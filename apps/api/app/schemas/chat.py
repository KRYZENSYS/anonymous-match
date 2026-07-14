"""Chat schemas."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


MessageType = Literal["text", "image", "video", "voice", "sticker", "gif", "file", "system"]


class MessageCreate(BaseModel):
    type: MessageType = "text"
    content: Optional[str] = None
    media_id: Optional[int] = None
    reply_to_id: Optional[int] = None
    extra: Optional[dict] = None


class MessageUpdate(BaseModel):
    content: str


class MediaInfo(BaseModel):
    id: int
    url: str
    thumbnail_url: Optional[str] = None
    type: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration_sec: Optional[int] = None


class MessagePublic(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    sender_public_id: str
    type: MessageType
    content: Optional[str] = None
    media: Optional[MediaInfo] = None
    reply_to: Optional["MessagePublic"] = None
    is_edited: bool
    is_deleted: bool
    is_mine: bool
    read_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: list[MessagePublic]
    total: int
    has_more: bool
    next_cursor: Optional[datetime] = None


class ChatPublic(BaseModel):
    id: int
    other_user_public_id: str
    other_user_nickname: str
    other_user_avatar: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    unread_count: int
    is_match: bool
    is_online: bool
    created_at: datetime


class ChatListResponse(BaseModel):
    chats: list[ChatPublic]
    total: int
    has_more: bool
