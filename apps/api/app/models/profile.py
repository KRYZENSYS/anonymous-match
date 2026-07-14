"""Profile modeli — foydalanuvchi ko'rinadigan ma'lumotlari (anonim)."""
from __future__ import annotations

from datetime import date
from sqlalchemy import String, Integer, Date, Text, ForeignKey, Float, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Profile(Base):
    """
    Foydalanuvchi profili — bu ma'lumotlar boshqalarga ko'rinadi.
    Hech qachon haqiqiy ism, telefon, telegram username ko'rinMAYDI.
    """
    __tablename__ = "profiles"
    __table_args__ = (
        # Postgres ARRAY uchun
        {"postgresql_with_oids": False},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Asosiy
    nickname: Mapped[str] = mapped_column(String(32), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Yosh va jins
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(Enum("male", "female", "other", name="gender_enum"), nullable=False)
    looking_for: Mapped[str] = mapped_column(
        Enum("male", "female", "everyone", name="looking_for_enum"), default="everyone", nullable=False
    )

    # Lokatsiya
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Qiziqishlar (array)
    interests: Mapped[list[str]] = mapped_column(ARRAY(String(32)), default=list, nullable=False)

    # Media
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    photos: Mapped[list[str]] = mapped_column(ARRAY(String(512)), default=list, nullable=False)  # 6 tagacha

    # Lifestyle
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(64), nullable=True)
    education: Mapped[str | None] = mapped_column(String(64), nullable=True)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String(8)), default=list, nullable=False)

    # Afzalliklar
    min_age_preference: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    max_age_preference: Mapped[int] = mapped_column(Integer, default=99, nullable=False)
    max_distance_km: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    show_only_online: Mapped[bool] = mapped_column(default=False, nullable=False)
    show_only_in_region: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Boost
    boost_expires_at: Mapped[Date | None] = mapped_column(Date, nullable=True)
    is_boosted: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Profil to'liq
    is_complete: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)  # foto orqali

    # Statistika
    profile_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    match_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Vaqt tamg'alari
    created_at: Mapped[Date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    updated_at: Mapped[Date] = mapped_column(
        Date, server_default=func.current_date(), onupdate=func.current_date(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="profile")

    def age(self) -> int | None:
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def __repr__(self) -> str:
        return f"<Profile user_id={self.user_id} nickname={self.nickname}>"
