"""Premium router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import User
from app.schemas.notification import PremiumStatus, PremiumPlansResponse, PremiumPlan, BoostResponse
from app.services.premium_service import PremiumService

router = APIRouter(prefix="/premium", tags=["Premium"])


@router.get("/status", response_model=PremiumStatus)
async def get_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    status_data = await PremiumService.get_status(db, user)
    return PremiumStatus(**status_data)


@router.get("/plans", response_model=PremiumPlansResponse)
async def get_plans():
    plans = await PremiumService.get_plans()
    return PremiumPlansResponse(plans=[PremiumPlan(**p) for p in plans])


@router.post("/boost", response_model=BoostResponse)
async def activate_boost(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await PremiumService.activate_boost(db, user)
    if not result["success"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, result["message"])
    return BoostResponse(**result)


@router.post("/verify-payment")
async def verify_payment(
    tier: str,
    duration_days: int,
    price_stars: int,
    payment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Telegram Stars to'lovini tekshirish va premium faollashtirish."""
    # TODO: Telegram Bot API orqali payment_id ni verify qilish
    from app.services.premium_service import PremiumService
    sub = await PremiumService.purchase(
        db, user, tier=tier,
        duration_days=duration_days,
        price_stars=price_stars,
        payment_id=payment_id,
    )
    return {
        "success": True,
        "subscription_id": sub.id,
        "tier": tier,
        "expires_at": sub.expires_at,
    }
