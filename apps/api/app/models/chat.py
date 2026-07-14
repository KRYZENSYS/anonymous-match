"""Chat, Message, Media — real-time chat tizimi."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, ForeignKey, Boolean, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Chat(Base):
    """Ikki foydalanuvchi o'rtasidagi chat (1:1)."""
    __tablename__ = "chats"
    __table_args__ = (
        # User pair unique
        {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Chat turi
    type: Mapped[str] = mapped_column(
        Enum("direct", "match", name="chat_type_enum"), default="direct", nullable=False
    )
    match_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True
    )

    # So'nggi faollik
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_message_preview: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # O'qilgan holat
    user1_unread: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user2_unread: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_archived_u1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_archived_u2: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="chats_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="chats_as_user2")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    match = relationship("Match", foreign_keys=[match_id])

    def get_other_user_id(self, current_user_id: int) -> int:
        return self.user2_id if current_user_id == self.user1_id else self.user1_id

    def get_unread_for(self, user_id: int) -> int:
        return self.user1_unread if user_id == self.user1_id else self.user2_unread

    def __repr__(self) -> str:
        return f"<Chat u1={self.user1_id} u2={self.user2_id}>"


class Message(Base):
    """Chat xabari."""
    __tablename__ = "messages"
    __table_args__ = (
        # Index for chat messages pagination
        {},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Turlar
    type: Mapped[str] = mapped_column(
        Enum("text", "image", "video", "voice", "sticker", "gif", "file", "system", name="message_type_enum"),
        default="text", nullable=False,
    )

    # Kontent
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("media.id", ondelete="SET NULL"), nullable=True
    )
    reply_to_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )

    # Qo'shimcha ma'lumot (metadata)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Status
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_for_everyone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # O'qilgan
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    media = relationship("Media", foreign_keys=[media_id])
    reply_to = relationship("Message", remote_side=[id], foreign_keys=[reply_to_id])

    def __repr__(self) -> str:
        return f"<Message id={self.id} chat={self.chat_id} type={self.type}>"


class Media(Base):
    """Yuklangan fayllar — rasm, video, voice, sticker."""
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    type: Mapped[str] = mapped_column(
        Enum("avatar", "photo", "video", "voice", "sticker", "gif", "file", name="media_type_enum"),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    public_id: Mapped[str | None] = mapped_column(String(128), nullable=True)  # Cloudinary public_id

    # Meta
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)  # voice/video

    # Moderatsiya
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_safe: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    moderation_score: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="media")

    def __repr__(self) -> str:
        return f"<Media id={self.id} type={self.type} user={self.user_id}>"
