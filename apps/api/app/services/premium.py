"""Premium service"""
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import select
from app.models.user import User
from app.models.subscription import Premium, Payment


PREMIUM_PLANS = {
    "plus": {"name": "Plus", "tier": "plus", "price_stars": 500, "price_usd": 9.99, "duration_days": 30, "features": ["Cheksiz yoqtirishlar", "10 super like / kun", "Reklama yo'q", "5 boost / oy"]},
    "gold": {"name": "Gold", "tier": "gold", "price_stars": 1200, "price_usd": 19.99, "duration_days": 30, "features": ["Plus ning barchasi", "30 super like / kun", "Kim ko'rganini bilish", "Yashirin rejim", "10 boost / oy"]},
    "platinum": {"name": "Platinum", "tier": "platinum", "price_stars": 2500, "price_usd": 39.99, "duration_days": 30, "features": ["Gold ning barchasi", "9999 super like / kun", "VIP badge", "Prioritet", "Cheksiz boost"]},
}


class PremiumService:
    @staticmethod
    async def get_status(session, user_id):
        result = await session.execute(select(Premium).where(Premium.user_id == user_id, Premium.expires_at > datetime.utcnow()).order_by(Premium.expires_at.desc()).limit(1))
        active = result.scalar_one_or_none()
        if not active:
            return {"is_premium": False, "tier": None, "expires_at": None, "days_left": 0, "boost_count": 0}
        return {"is_premium": True, "tier": active.tier, "expires_at": active.expires_at, "days_left": max(0, (active.expires_at - datetime.utcnow()).days), "boost_count": active.boost_count or 0}

    @staticmethod
    async def get_plans():
        return list(PREMIUM_PLANS.values())

    @staticmethod
    async def verify_and_activate(session, user_id, tier, duration_days, amount_paid, payment_id):
        if tier not in PREMIUM_PLANS:
            return {"success": False, "message": "Invalid tier"}
        payment = Payment(user_id=user_id, tier=tier, amount_stars=amount_paid, amount_usd=PREMIUM_PLANS[tier]["price_usd"], telegram_payment_charge_id=payment_id, status="completed")
        session.add(payment)
        result = await session.execute(select(Premium).where(Premium.user_id == user_id, Premium.expires_at > datetime.utcnow()).order_by(Premium.expires_at.desc()).limit(1))
        existing = result.scalar_one_or_none()
        if existing and existing.tier == tier:
            existing.expires_at = existing.expires_at + timedelta(days=duration_days)
            existing.boost_count = (existing.boost_count or 0) + (5 if tier == "plus" else 10 if tier == "gold" else 99)
        else:
            premium = Premium(user_id=user_id, tier=tier, expires_at=datetime.utcnow() + timedelta(days=duration_days), boost_count=5 if tier == "plus" else 10 if tier == "gold" else 99)
            session.add(premium)
        user = await session.get(User, user_id)
        if user:
            user.is_premium = True
            user.premium_tier = tier
        await session.commit()
        return {"success": True, "tier": tier, "days": duration_days}

    @staticmethod
    async def use_boost(session, user_id):
        result = await session.execute(select(Premium).where(Premium.user_id == user_id, Premium.expires_at > datetime.utcnow()).order_by(Premium.expires_at.desc()).limit(1))
        premium = result.scalar_one_or_none()
        if not premium or (premium.boost_count or 0) <= 0:
            return {"success": False, "message": "Boost yo'q"}
        premium.boost_count -= 1
        user = await session.get(User, user_id)
        if user:
            user.is_boosted = True
            user.boost_expires_at = datetime.utcnow() + timedelta(minutes=30)
        await session.commit()
        return {"success": True, "remaining_boosts": premium.boost_count}
