"""User service"""
import random
import string
from datetime import datetime, date
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


def generate_public_id() -> str:
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f"AM-{suffix}"


def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


class UserService:
    @staticmethod
    async def get_or_create(session, telegram_id, first_name=None, last_name=None, username=None, language_code="uz", is_premium=False):
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            user.last_seen = datetime.utcnow()
            if first_name and not user.first_name:
                user.first_name = first_name
            await session.commit()
            return user, False
        user = User(
            telegram_id=telegram_id, public_id=generate_public_id(),
            first_name=first_name, last_name=last_name, username=username,
            language_code=language_code or "uz", is_premium=is_premium,
            last_seen=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user, True

    @staticmethod
    async def update_profile(session, user, data):
        from app.models.profile import Profile
        result = await session.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalar_one_or_none()
        if not profile:
            profile = Profile(user_id=user.id)
            session.add(profile)
        for field in ("nickname", "bio", "gender", "looking_for", "region", "city", "language_code"):
            if field in data and data[field] is not None:
                setattr(user, field, data[field])
        if "birth_date" in data and data["birth_date"]:
            bd = data["birth_date"]
            if isinstance(bd, str):
                bd = date.fromisoformat(bd)
            user.birth_date = bd
        if "interests" in data:
            user.interests = data["interests"] or []
        if "photos" in data:
            user.photos = data["photos"] or []
        if "height_cm" in data:
            profile.height_cm = data["height_cm"]
        if "occupation" in data:
            profile.occupation = data["occupation"]
        user.is_profile_complete = all([user.nickname, user.birth_date, user.gender, user.region, user.interests and len(user.interests) >= 3, user.photos and len(user.photos) >= 1])
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update_language(session, user, lang):
        if lang in ("uz", "ru", "en"):
            user.language_code = lang
            await session.commit()

    @staticmethod
    async def update_location(session, user, lat, lon):
        from app.models.profile import Profile
        result = await session.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalar_one_or_none()
        if not profile:
            profile = Profile(user_id=user.id)
            session.add(profile)
        profile.latitude = lat
        profile.longitude = lon
        await session.commit()
