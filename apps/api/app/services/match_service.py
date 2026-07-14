"""Match service — swipe, like, superlike, match yaratish."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_, or_, func, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.redis_client import get_redis
from app.models import User, Profile, Like, Match, Chat, Block
from app.schemas.match import SwipeResponse, SwipeRequest, MatchPublic
from app.schemas.user import ProfilePublic

logger = logging.getLogger(__name__)


class MatchService:
    """Match va swipe tizimi."""

    @staticmethod
    async def get_discover_profiles(
        db: AsyncSession,
        user: User,
        min_age: int = 18,
        max_age: int = 99,
        gender: str = "any",
        region: Optional[str] = None,
        city: Optional[str] = None,
        online_only: bool = False,
        interests: Optional[list[str]] = None,
        limit: int = 20,
    ) -> list[Profile]:
        today = datetime.utcnow().date()
        min_birth = today.replace(year=today.year - max_age)
        max_birth = today.replace(year=today.year - min_age)

        q = (
            select(Profile)
            .join(User, User.id == Profile.user_id)
            .where(
                Profile.user_id != user.id,
                Profile.is_complete == True,
                User.is_banned == False,
                User.is_suspended == False,
                Profile.birth_date.between(min_birth, max_birth),
            )
            .options(selectinload(Profile.user))
        )

        if gender in ("male", "female", "other"):
            q = q.where(Profile.gender == gender)
        if region:
            q = q.where(Profile.region == region)
        if city:
            q = q.where(Profile.city == city)
        if online_only:
            q = q.where(User.is_online == True)
        if interests:
            q = q.where(Profile.interests.op("&&")(interests))

        # Boost qilinganlarni birinchi
        q = q.order_by(Profile.is_boosted.desc(), func.random())

        # Allaqachon swipe qilinganlarni chiqarib tashlash
        swiped_sub = select(Like.to_user_id).where(Like.from_user_id == user.id)
        q = q.where(Profile.user_id.notin_(swiped_sub))

        blocked_sub = select(Block.blocked_id).where(Block.blocker_id == user.id)
        blocked_by_sub = select(Block.blocker_id).where(Block.blocked_id == user.id)
        q = q.where(Profile.user_id.notin_(blocked_sub))
        q = q.where(Profile.user_id.notin_(blocked_by_sub))

        q = q.limit(limit)
        res = await db.execute(q)
        return list(res.scalars().all())

    @staticmethod
    async def swipe(
        db: AsyncSession,
        user: User,
        request: SwipeRequest,
    ) -> SwipeResponse:
        if request.target_user_id == user.id:
            raise ValueError("O'zingizga swipe qila olmaysiz")

        redis = get_redis()
        today = datetime.utcnow().strftime("%Y-%m-%d")

        is_premium = await MatchService._is_premium(db, user)
        daily_limit = 999 if is_premium else settings.LIKES_DAILY_FREE
        superlike_limit = 999 if is_premium else settings.SUPERLIKE_DAILY_FREE

        likes_key = f"swipes:{user.id}:{today}:likes"
        super_key = f"swipes:{user.id}:{today}:super"

        if request.action in ("like", "superlike"):
            count = await redis.incr(likes_key)
            if count == 1:
                await redis.expire(likes_key, 86400)
            if not is_premium and count > daily_limit:
                return SwipeResponse(
                    success=False,
                    is_match=False,
                    remaining_likes=0,
                    remaining_superlikes=0,
                    message="Kunlik like limiti tugadi. Premium ga o'ting!",
                )

            if request.action == "superlike":
                sc = await redis.incr(super_key)
                if sc == 1:
                    await redis.expire(super_key, 86400)
                if not is_premium and sc > superlike_limit:
                    return SwipeResponse(
                        success=False,
                        is_match=False,
                        remaining_likes=daily_limit - count,
                        remaining_superlikes=0,
                        message="Kunlik superlike limiti tugadi",
                    )

        existing = await db.execute(
            select(Like).where(
                Like.from_user_id == user.id,
                Like.to_user_id == request.target_user_id,
            )
        )
        if existing.scalar_one_or_none():
            return SwipeResponse(
                success=False,
                is_match=False,
                remaining_likes=0,
                remaining_superlikes=0,
                message="Allaqachon swipe qilgansiz",
            )

        like = Like(
            from_user_id=user.id,
            to_user_id=request.target_user_id,
            action=request.action,
        )
        db.add(like)

        await db.execute(
            Profile.__table__.update()
            .where(Profile.user_id == request.target_user_id)
            .values(profile_views=Profile.profile_views + 1)
        )

        is_match = False
        match_id = None
        chat_id = None

        if request.action in ("like", "superlike"):
            reverse = await db.execute(
                select(Like).where(
                    Like.from_user_id == request.target_user_id,
                    Like.to_user_id == user.id,
                    Like.action.in_(["like", "superlike"]),
                )
            )
            reverse_like = reverse.scalar_one_or_none()
            if reverse_like:
                is_match = True
                like.is_mutual = True
                reverse_like.is_mutual = True

                u1, u2 = sorted([user.id, request.target_user_id])
                existing_match = await db.execute(
                    select(Match).where(Match.user1_id == u1, Match.user2_id == u2)
                )
                match = existing_match.scalar_one_or_none()
                if not match:
                    match = Match(user1_id=u1, user2_id=u2, initiated_by=user.id)
                    db.add(match)
                    await db.flush()

                    chat = Chat(user1_id=u1, user2_id=u2, type="match", match_id=match.id)
                    db.add(chat)
                    await db.flush()
                    match.chat_id = chat.id

                match_id = match.id
                chat_id = match.chat_id

        if request.action in ("like", "superlike"):
            await db.execute(
                Profile.__table__.update()
                .where(Profile.user_id == user.id)
                .values(likes_sent=Profile.likes_sent + 1)
            )
            await db.execute(
                Profile.__table__.update()
                .where(Profile.user_id == request.target_user_id)
                .values(likes_received=Profile.likes_received + 1)
            )

        await db.flush()

        # Qolgan limitlar
        try:
            likes_val = await redis.get(likes_key)
            super_val = await redis.get(super_key)
            remaining_likes = max(0, daily_limit - int(likes_val or 0))
            remaining_super = max(0, superlike_limit - int(super_val or 0))
        except Exception:
            remaining_likes = daily_limit
            remaining_super = superlike_limit

        return SwipeResponse(
            success=True,
            is_match=is_match,
            match_id=match_id,
            chat_id=chat_id,
            remaining_likes=remaining_likes,
            remaining_superlikes=remaining_super,
            message="🎉 Bu MATCH! Bir-biringizga yoqdingiz!" if is_match else None,
        )

    @staticmethod
    async def get_my_matches(db: AsyncSession, user: User) -> list[MatchPublic]:
        res = await db.execute(
            select(Match)
            .where(
                or_(Match.user1_id == user.id, Match.user2_id == user.id),
                Match.is_active == True,
                Match.is_unmatched == False,
            )
            .order_by(Match.matched_at.desc())
        )
        matches = res.scalars().all()

        result = []
        for m in matches:
            other_id = m.get_other_user_id(user.id)
            other_user = await db.execute(
                select(User).options(selectinload(User.profile)).where(User.id == other_id)
            )
            other = other_user.scalar_one()
            if not other.profile:
                continue

            is_prem = False
            if hasattr(other, "premium") and other.premium:
                is_prem = other.premium.is_active

            other_profile = ProfilePublic.model_validate({
                "public_id": other.public_id,
                "nickname": other.profile.nickname,
                "age": other.profile.age(),
                "gender": other.profile.gender,
                "looking_for": other.profile.looking_for,
                "region": other.profile.region,
                "city": other.profile.city,
                "interests": other.profile.interests or [],
                "avatar_url": other.profile.avatar_url,
                "photos": other.profile.photos or [],
                "height_cm": other.profile.height_cm,
                "occupation": other.profile.occupation,
                "education": other.profile.education,
                "languages": other.profile.languages or [],
                "bio": other.profile.bio,
                "is_online": other.is_online,
                "last_seen": other.last_seen,
                "is_verified": other.profile.is_verified,
                "is_premium": is_prem,
                "is_boosted": other.profile.is_boosted,
                "distance_km": None,
            })

            preview = None
            if m.chat:
                preview = m.chat.last_message_preview

            result.append(MatchPublic(
                id=m.id,
                matched_at=m.matched_at,
                is_new=not m.first_message_sent,
                other_user=other_profile,
                last_message_at=m.chat.last_message_at if m.chat else None,
                last_message_preview=preview,
                unread_count=m.chat.get_unread_for(user.id) if m.chat else 0,
                is_first_message=not m.first_message_sent,
            ))

        return result

    @staticmethod
    async def _is_premium(db: AsyncSession, user: User) -> bool:
        from app.services.premium_service import PremiumService
        return await PremiumService.is_premium(db, user)
