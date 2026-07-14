"""Payments service - Telegram Stars, TON, Stripe"""
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.subscription import Premium, Payment
from app.models.user import User
from app.models.gamification import CoinTransaction
from app.models.seasonal import SubscriptionPlan
from app.core.config import settings


class PaymentService:
    """Handle payments: Telegram Stars, TON, Stripe"""

    @staticmethod
    async def create_telegram_stars_invoice(
        session: AsyncSession, user_id: int, plan_code: str, amount: int
    ) -> dict:
        """Create Telegram Stars invoice link"""
        payload = f"{user_id}:{plan_code}:{secrets.token_hex(8)}"
        # In production: create via Bot API
        # bot.create_invoice_link(...)
        return {
            "invoice_link": f"https://t.me/$invoice_{payload}",
            "payload": payload,
            "amount": amount,
        }

    @staticmethod
    async def verify_telegram_payment(payload: dict) -> bool:
        """Verify Telegram Stars payment notification"""
        # Validate via Telegram Bot API: getStarTransactions
        bot_token = settings.BOT_TOKEN
        if not bot_token:
            return False
        try:
            import aiohttp
            # Call Telegram API
            url = f"https://api.telegram.org/bot{bot_token}/getStarTransactions"
            async with aiohttp.ClientSession() as s:
                async with s.post(url) as resp:
                    data = await resp.json()
                    return data.get("ok", False)
        except Exception:
            return False

    @staticmethod
    async def activate_premium(
        session: AsyncSession, user_id: int, plan_code: str, duration_days: int, payment_id: int
    ) -> Premium:
        """Activate premium subscription"""
        r = await session.execute(select(Premium).where(Premium.user_id == user_id))
        existing = r.scalar_one_or_none()
        now = datetime.utcnow()
        if existing and existing.is_active and existing.expires_at > now:
            # Extend
            existing.expires_at = max(existing.expires_at, now) + timedelta(days=duration_days)
            existing.plan_code = plan_code
        else:
            if not existing:
                existing = Premium(
                    user_id=user_id, plan_code=plan_code, tier=1,
                    started_at=now, expires_at=now + timedelta(days=duration_days),
                    is_active=True,
                )
                session.add(existing)
            else:
                existing.plan_code = plan_code
                existing.started_at = now
                existing.expires_at = now + timedelta(days=duration_days)
                existing.is_active = True
        # Update user
        user = await session.get(User, user_id)
        if user:
            user.is_premium = True
        # Mark payment complete
        p = await session.get(Payment, payment_id)
        if p:
            p.status = "completed"
        await session.commit()
        return existing

    @staticmethod
    async def create_ton_invoice(session: AsyncSession, user_id: int, amount_ton: float, plan_code: str) -> dict:
        """Create TON payment invoice"""
        payload = f"ton_{user_id}_{plan_code}_{secrets.token_hex(4)}"
        # TON wallet address
        return {
            "wallet": settings.TON_WALLET_ADDRESS or "UQB...WALLET",
            "amount": amount_ton,
            "payload": payload,
            "comment": f"AnonymousMatch {plan_code}",
        }

    @staticmethod
    async def verify_ton_payment(payload: str, transaction_hash: str) -> bool:
        """Verify TON transaction"""
        # Use TON API: https://toncenter.com/api/v2/
        try:
            import aiohttp
            url = f"https://toncenter.com/api/v2/getTransactions"
            params = {"address": settings.TON_WALLET_ADDRESS, "limit": 10}
            async with aiohttp.ClientSession() as s:
                async with s.get(url, params=params) as resp:
                    data = await resp.json()
                    # Check if transaction exists with our payload
                    for tx in data.get("result", []):
                        if transaction_hash in str(tx):
                            return True
            return False
        except Exception:
            return False

    @staticmethod
    async def create_stripe_session(plan_code: str, amount_usd: float) -> dict:
        """Create Stripe checkout session"""
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"AnonymousMatch {plan_code}"},
                        "unit_amount": int(amount_usd * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="https://anonymous-match.uz/success",
                cancel_url="https://anonymous-match.uz/cancel",
            )
            return {"url": session.url, "session_id": session.id}
        except Exception as e:
            return {"url": None, "error": str(e)}

    @staticmethod
    async def purchase_coins(
        session: AsyncSession, user_id: int, package_id: int, telegram_payment_charge_id: str
    ) -> int:
        """Buy coin package"""
        from app.models.community import CoinPackage
        p = await session.get(CoinPackage, package_id)
        if not p:
            raise ValueError("Package not found")
        total = p.coins + (p.bonus_coins or 0)
        session.add(CoinTransaction(
            user_id=user_id, amount=total, type="purchase",
            reason=f"Coin package: {p.name}",
        ))
        await session.commit()
        return total

    @staticmethod
    async def webhook_handler(session: AsyncSession, payload: dict, signature: str = None) -> bool:
        """Handle Telegram payment webhook"""
        # Verify signature
        if signature and settings.WEBHOOK_SECRET:
            expected = hmac.new(settings.WEBHOOK_SECRET.encode(), json.dumps(payload).encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, signature):
                return False
        # Process
        try:
            event_type = payload.get("event_type")
            if event_type == "payment_succeeded":
                user_id = int(payload.get("payload", "0:plan:0").split(":")[0])
                plan_code = payload.get("payload", "0:plan:0").split(":")[1]
                charge_id = payload.get("telegram_payment_charge_id", "")
                # Find or create payment
                p = Payment(
                    user_id=user_id, tier=plan_code, amount_stars=payload.get("amount", 0),
                    telegram_payment_charge_id=charge_id, status="completed",
                )
                session.add(p)
                await session.flush()
                # Activate
                r = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.code == plan_code))
                plan = r.scalar_one_or_none()
                if plan:
                    await PaymentService.activate_premium(session, user_id, plan_code, plan.duration_days, p.id)
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            return False
