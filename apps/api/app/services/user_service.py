"""User service — foydalanuvchi bilan bog'liq biznes logika."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import generate_public_id, create_access_token
from app.models import User, Profile, Premium, Log
from app.schemas.user import ProfileUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Foydalanuvchi servisi."""

    @staticmethod
    async def get_or_create_from_telegram(
        db: AsyncSession,
        telegram_data: dict,
        device_id: Optional[str] = None,
        webapp_version: Optional[str] = None,
    ) -> tuple[User, bool]:
        tg_user = telegram_data.get("user", {})
        telegram_id = int(tg_user.get("id", 0))
        if not telegram_id:
            raise ValueError("Telegram ID topilmadi")

        res = await db.execute(
            select(User).options(selectinload(User.profile), selectinload(User.premium))
            .where(User.telegram_id == telegram_id)
        )
        user = res.scalar_one_or_none()

        is_new = False
        if not user:
            is_new = True
            is_admin = telegram_id in settings.admin_ids
            user = User(
                telegram_id=telegram_id,
                telegram_username=tg_user.get("username"),
                telegram_first_name=tg_user.get("first_name"),
                telegram_photo_url=tg_user.get("photo_url"),
                telegram_language_code=tg_user.get("language_code", "uz"),
                is_telegram_premium=tg_user.get("is_premium", False),
                public_id=generate_public_id(),
                role="admin" if is_admin else "user",
                is_admin=is_admin,
                device_id=device_id,
                webapp_version=webapp_version,
                preferred_language=tg_user.get("language_code", "uz") if tg_user.get("language_code") in ["uz", "ru", "en"] else "uz",
            )
            db.add(user)
            await db.flush()

            premium = Premium(user_id=user.id)
            db.add(premium)

            db.add(Log(
                user_id=user.id,
                level="info",
                category="auth",
                action="register",
                message="Yangi foydalanuvchi ro'yxatdan o'tdi",
                details={"telegram_id": telegram_id, "is_admin": is_admin},
            ))
        else:
            user.telegram_username = tg_user.get("username") or user.telegram_username
            user.telegram_first_name = tg_user.get("first_name") or user.telegram_first_name
            user.telegram_photo_url = tg_user.get("photo_url") or user.telegram_photo_url
            user.is_telegram_premium = tg_user.get("is_premium", False)
            user.is_online = True
            user.last_active_at = datetime.utcnow()
            if device_id:
                user.device_id = device_id
            if webapp_version:
                user.webapp_version = webapp_version

        if telegram_id in settings.admin_ids and not user.is_admin:
            user.is_admin = True
            user.role = "admin"

        await db.flush()
        return user, is_new

    @staticmethod
    def create_token(user: User) -> tuple[str, int]:
        token = create_access_token(
            subject=user.id,
            extra={"public_id": user.public_id, "is_admin": user.is_admin},
        )
        return token, settings.JWT_ACCESS_TTL_HOURS * 3600

    @staticmethod
    async def update_profile(
        db: AsyncSession, user: User, data: ProfileUpdate
    ) -> Profile:
        res = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = res.scalar_one_or_none()

        if not profile:
            profile = Profile(
                user_id=user.id,
                nickname=data.nickname or f"user_{user.public_id[-4:]}",
                birth_date=data.birth_date or datetime(2000, 1, 1).date(),
                gender=data.gender or "other",
            )
            db.add(profile)

        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            if v is not None:
                setattr(profile, k, v)

        if profile.nickname and profile.birth_date and profile.gender and profile.photos:
            profile.is_complete = True

        await db.flush()
        return profile

    @staticmethod
    async def update_location(db: AsyncSession, user: User, lat: float, lon: float):
        res = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = res.scalar_one_or_none()
        if profile:
            profile.latitude = lat
            profile.longitude = lon
            await db.flush()

    @staticmethod
    async def get_profile(db: AsyncSession, user: User) -> Profile | None:
        res = await db.execute(select(Profile).where(Profile.user_id == user.id))
        return res.scalar_one_or_none()

    @staticmethod
    async def set_online(db: AsyncSession, user: User, online: bool = True):
        user.is_online = online
        user.last_active_at = datetime.utcnow()
        await db.flush()

    @staticmethod
    async def set_preferred_language(db: AsyncSession, user: User, lang: str):
        if lang in ("uz", "ru", "en"):
            user.preferred_language = lang
            await db.flush()

    @staticmethod
    async def set_theme(db: AsyncSession, user: User, theme: str):
        if theme in ("dark", "light", "auto"):
            user.theme = theme
            await db.flush()
