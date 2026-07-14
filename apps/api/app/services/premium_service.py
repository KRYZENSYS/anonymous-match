"""Premium service — obuna, boost, super like."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import User, Premium, Subscription, Log, Profile

logger = logging.getLogger(__name__)


class PremiumService:
    @staticmethod
    async def is_premium(db: AsyncSession, user: User) -> bool:
        res = await db.execute(select(Premium).where(Premium.user_id == user.id))
        prem = res.scalar_one_or_none()
        if not prem or not prem.is_premium:
            return False
        if prem.expires_at and prem.expires_at < datetime.utcnow():
            prem.is_premium = False
            prem.is_active = False
            return False
        return prem.is_active

    @staticmethod
    async def get_status(db: AsyncSession, user: User) -> dict:
        res = await db.execute(select(Premium).where(Premium.user_id == user.id))
        prem = res.scalar_one_or_none()
        if not prem:
            prem = Premium(user_id=user.id)
            db.add(prem)
            await db.flush()

        days_left = 0
        if prem.expires_at and prem.is_active:
            days_left = max(0, (prem.expires_at - datetime.utcnow()).days)

        return {
            "is_premium": prem.is_active,
            "tier": prem.tier,
            "started_at": prem.started_at,
            "expires_at": prem.expires_at,
            "days_left": days_left,
            "auto_renew": prem.auto_renew,
            "super_likes_remaining": max(0, prem.super_likes_limit - prem.super_likes_used),
            "likes_remaining": max(0, prem.likes_limit - prem.likes_used_today),
            "boost_count": prem.boost_count,
            "last_boost_at": prem.last_boost_at,
        }

    @staticmethod
    async def purchase(
        db: AsyncSession,
        user: User,
        tier: str,
        duration_days: int = 30,
        price_stars: int = 500,
        payment_id: Optional[str] = None,
    ) -> Subscription:
        sub = Subscription(
            user_id=user.id,
            tier=tier,
            duration_days=duration_days,
            price_stars=price_stars,
            status="active",
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=duration_days),
            payment_id=payment_id,
        )
        db.add(sub)

        res = await db.execute(select(Premium).where(Premium.user_id == user.id))
        prem = res.scalar_one_or_none()
        if not prem:
            prem = Premium(user_id=user.id)
            db.add(prem)

        now = datetime.utcnow()
        base = prem.expires_at if (prem.is_active and prem.expires_at and prem.expires_at > now) else now
        new_expires = base + timedelta(days=duration_days)

        prem.is_premium = True
        prem.is_active = True
        prem.tier = tier
        prem.started_at = prem.started_at or now
        prem.expires_at = new_expires
        prem.likes_limit = 9999 if tier in ("gold", "platinum") else 100
        prem.super_likes_limit = 9999 if tier == "platinum" else (10 if tier == "gold" else 3)

        db.add(Log(
            user_id=user.id,
            level="info",
            category="payment",
            action="premium_purchase",
            message=f"Premium sotib olindi: {tier}",
            details={"tier": tier, "duration_days": duration_days, "price_stars": price_stars},
        ))

        await db.flush()
        return sub

    @staticmethod
    async def activate_boost(db: AsyncSession, user: User) -> dict:
        res = await db.execute(select(Premium).where(Premium.user_id == user.id))
        prem = res.scalar_one_or_none()
        if not prem:
            return {"success": False, "message": "Premium topilmadi", "remaining_boosts": 0}
        if prem.boost_count <= 0:
            return {"success": False, "message": "Boost limiti tugadi", "remaining_boosts": 0}

        expires = datetime.utcnow() + timedelta(minutes=settings.BOOST_DURATION_MINUTES)
        prem.boost_count -= 1
        prem.last_boost_at = datetime.utcnow()

        res2 = await db.execute(select(Profile).where(Profile.user_id == user.id))
        prof = res2.scalar_one_or_none()
        if prof:
            prof.is_boosted = True
            prof.boost_expires_at = expires.date()

        db.add(Log(
            user_id=user.id,
            level="info",
            category="payment",
            action="boost_activated",
            message="Boost faollashtirildi",
            details={"expires_at": expires.isoformat()},
        ))

        await db.flush()
        return {
            "success": True,
            "boost_expires_at": expires,
            "remaining_boosts": prem.boost_count,
            "message": "Boost faollashtirildi",
        }

    @staticmethod
    async def get_plans() -> list[dict]:
        return [
            {
                "tier": "plus", "name": "Plus", "duration_days": 30,
                "price_stars": 500, "price_usd": 5.99,
                "features": ["Unlimited likes", "5 super likes / hafta", "Reklama yo'q", "Boost har oyda 1 marta"],
            },
            {
                "tier": "gold", "name": "Gold", "duration_days": 30,
                "price_stars": 1200, "price_usd": 14.99,
                "features": ["Plus hammasi", "10 super likes / hafta", "Kim profilingni ko'rgan", "Boost 3 marta/oy", "Bevosita chat"],
            },
            {
                "tier": "platinum", "name": "Platinum", "duration_days": 30,
                "price_stars": 2500, "price_usd": 29.99,
                "features": ["Gold hammasi", "Cheksiz super likes", "VIP Badge", "Boost har hafta", "Prioritet ko'rinish", "Maxsus support"],
            },
        ]
