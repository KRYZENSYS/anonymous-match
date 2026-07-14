"""Premium va Subscription — pullik obuna."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Premium(Base):
    """Foydalanuvchining joriy premium holati."""
    __tablename__ = "premium"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tier: Mapped[str] = mapped_column(
        Enum("none", "plus", "gold", "platinum", name="premium_tier_enum"),
        default="none", nullable=False
    )

    # Vaqt
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Boost
    boost_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_boost_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Statistika
    super_likes_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    super_likes_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # kunlik
    likes_used_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes_limit: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    likes_reset_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Ko'rishlar
    profile_views_seen: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Auto-renew
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="premium")

    def __repr__(self) -> str:
        return f"<Premium user={self.user_id} tier={self.tier} active={self.is_active}>"


class Subscription(Base):
    """Obuna tarixi — har bir to'lov alohida yoziladi."""
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Tarif
    tier: Mapped[str] = mapped_column(String(16), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price_stars: Mapped[int] = mapped_column(Integer, nullable=False)  # Telegram Stars
    price_usd: Mapped[float] = mapped_column(default=0.0, nullable=False)

    # To'lov
    payment_method: Mapped[str] = mapped_column(
        Enum("telegram_stars", "card", "crypto", "admin_grant", name="payment_method_enum"),
        default="telegram_stars", nullable=False
    )
    payment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)  # Telegram payment id
    payment_charge_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        Enum("pending", "paid", "active", "expired", "cancelled", "refunded", name="subscription_status_enum"),
        default="pending", nullable=False
    )

    # Vaqt
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription user={self.user_id} tier={self.tier} status={self.status}>"
