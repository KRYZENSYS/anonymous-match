"""User modeli — foydalanuvchi asosiy ma'lumotlari."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    Foydalanuvchi modeli.
    Telegram orqali avtomatik ro'yxatdan o'tadi.
    """
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_telegram_id", "telegram_id", unique=True),
        Index("ix_users_public_id", "public_id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Telegram ma'lumotlari (YASHIRIN — faqat backend uchun)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    telegram_first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    telegram_photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    telegram_language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_telegram_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    # Anonim identifikator
    public_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)

    # Rol va status
    role: Mapped[str] = mapped_column(String(16), default="user", nullable=False)  # user | moderator | admin
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suspended_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ban_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Faollik
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Qurilma / sessiya
    device_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    push_token: Mapped[str | None] = mapped_column(String(256), nullable=True)
    webapp_version: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # Lokal
    preferred_language: Mapped[str] = mapped_column(String(8), default="uz", nullable=False)
    theme: Mapped[str] = mapped_column(String(8), default="dark", nullable=False)  # dark | light | auto

    # Vaqt tamg'alari
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ===== Relationships =====
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_likes = relationship("Like", foreign_keys="Like.from_user_id", back_populates="from_user", cascade="all, delete-orphan")
    received_likes = relationship("Like", foreign_keys="Like.to_user_id", back_populates="to_user", cascade="all, delete-orphan")
    matches_as_user1 = relationship("Match", foreign_keys="Match.user1_id", back_populates="user1", cascade="all, delete-orphan")
    matches_as_user2 = relationship("Match", foreign_keys="Match.user2_id", back_populates="user2", cascade="all, delete-orphan")
    chats_as_user1 = relationship("Chat", foreign_keys="Chat.user1_id", back_populates="user1", cascade="all, delete-orphan")
    chats_as_user2 = relationship("Chat", foreign_keys="Chat.user2_id", back_populates="user2", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    sent_reports = relationship("Report", foreign_keys="Report.reporter_id", back_populates="reporter", cascade="all, delete-orphan")
    received_reports = relationship("Report", foreign_keys="Report.reported_id", back_populates="reported", cascade="all, delete-orphan")
    blocked_users = relationship("Block", foreign_keys="Block.blocker_id", back_populates="blocker", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    premium = relationship("Premium", back_populates="user", uselist=False, cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} public_id={self.public_id}>"
