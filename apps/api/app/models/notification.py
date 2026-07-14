"""Notification modeli — bildirishnomalar."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Notification(Base):
    """Foydalanuvchiga bildirishnoma."""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Turi
    type: Mapped[str] = mapped_column(
        Enum(
            "new_match", "new_message", "new_like", "super_like", "profile_view",
            "chat_request", "boost_active", "premium_expiring", "system",
            "announcement", "report_resolved",
            name="notification_type_enum"
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(128), nullable=False)
    body: Mapped[str] = mapped_column(String(512), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(8), nullable=True)  # emoji

    # Qo'shimcha ma'lumot
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Bog'langan obyektlar
    related_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    related_chat_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    related_match_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Holat
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Yetkazish
    sent_push: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_telegram: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification type={self.type} user={self.user_id}>"
