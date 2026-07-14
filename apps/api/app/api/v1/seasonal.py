"""Seasonal, travel, anonymous mode, charity, AB test, ad endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.models.seasonal import (
    SeasonalEvent, TravelMode, CharityDonation, AnonymousProfile,
    ABTest, ABTestAssignment, ABTestEvent, SubscriptionPlan, AdCampaign, SponsoredProfile,
)

router = APIRouter(prefix="/seasonal", tags=["seasonal"])


# ===== Seasonal Events =====
@router.get("/events")
async def active_seasonal_events(session: AsyncSession = Depends(get_session)):
    now = datetime.utcnow()
    r = await session.execute(select(SeasonalEvent).where(SeasonalEvent.is_active == True, SeasonalEvent.starts_at <= now, SeasonalEvent.ends_at >= now))
    return [{"id": e.id, "name": e.name, "code": e.code, "description": e.description, "icon": e.icon, "theme_color": e.theme_color, "bonus_multiplier": e.bonus_multiplier, "special_features": e.special_features, "ends_at": e.ends_at} for e in r.scalars().all()]


# ===== Travel Mode =====
@router.post("/travel")
async def enable_travel(city: str, country: str, lat: float = None, lon: float = None, days: int = 7, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from datetime import timedelta
    r = await session.execute(select(TravelMode).where(TravelMode.user_id == current_user.id))
    tm = r.scalar_one_or_none()
    if tm:
        tm.current_city = city
        tm.current_country = country
        tm.current_lat = lat
        tm.current_lon = lon
        tm.expires_at = datetime.utcnow() + timedelta(days=days)
        tm.is_active = True
    else:
        session.add(TravelMode(user_id=current_user.id, current_city=city, current_country=country, current_lat=lat, current_lon=lon, expires_at=datetime.utcnow() + timedelta(days=days), is_active=True))
    await session.commit()
    return {"city": city, "country": country, "expires_at": datetime.utcnow() + timedelta(days=days)}


@router.delete("/travel")
async def disable_travel(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(TravelMode).where(TravelMode.user_id == current_user.id))
    tm = r.scalar_one_or_none()
    if tm:
        tm.is_active = False
    await session.commit()
    return {"ok": True}


# ===== Anonymous Mode =====
@router.get("/anonymous")
async def get_anonymous_settings(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(AnonymousProfile).where(AnonymousProfile.user_id == current_user.id))
    a = r.scalar_one_or_none()
    if not a:
        return {"is_anonymous": False, "incognito_mode": False, "hide_from_feed": False, "hide_distance": False, "hide_age": False, "hide_last_seen": False}
    return {"is_anonymous": a.is_anonymous, "anonymous_avatar": a.anonymous_avatar, "incognito_mode": a.incognito_mode, "hide_from_feed": a.hide_from_feed, "hide_distance": a.hide_distance, "hide_age": a.hide_age, "hide_last_seen": a.hide_last_seen}


@router.post("/anonymous")
async def update_anonymous(data: dict, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(AnonymousProfile).where(AnonymousProfile.user_id == current_user.id))
    a = r.scalar_one_or_none()
    if not a:
        a = AnonymousProfile(user_id=current_user.id, **data)
        session.add(a)
    else:
        for k, v in data.items():
            if hasattr(a, k):
                setattr(a, k, v)
    await session.commit()
    return {"ok": True}


# ===== Charity =====
@router.post("/charity/donate")
async def donate(match_id: int, amount_usd: float, charity: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if not current_user.is_premium:
        raise HTTPException(403, "Premium only")
    d = CharityDonation(user_id=current_user.id, match_id=match_id, amount_usd=amount_usd, charity=charity)
    session.add(d)
    await session.commit()
    return {"ok": True, "charity": charity, "amount": amount_usd}


@router.get("/charity/stats")
async def charity_stats(session: AsyncSession = Depends(get_session)):
    from sqlalchemy import func
    r = await session.execute(select(CharityDonation.charity, func.sum(CharityDonation.amount_usd).label("total"), func.count(CharityDonation.id).label("count")).group_by(CharityDonation.charity))
    return [{"charity": c, "total_usd": float(t or 0), "donations": cnt} for c, t, cnt in r.all()]


# ===== A/B Test =====
@router.post("/ab/track")
async def ab_track(test_name: str, event_name: str, value: float = 0.0, metadata: dict = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(ABTest).where(ABTest.name == test_name, ABTest.is_active == True))
    test = r.scalar_one_or_none()
    if not test:
        return {"ok": False}
    r2 = await session.execute(select(ABTestAssignment).where(ABTestAssignment.user_id == current_user.id, ABTestAssignment.test_id == test.id))
    assignment = r2.scalar_one_or_none()
    if not assignment:
        import random
        variants = test.variants if isinstance(test.variants, list) else []
        if not variants:
            return {"ok": False}
        weights = [v.get("weight", 0.5) if isinstance(v, dict) else 0.5 for v in variants]
        chosen = random.choices([v.get("name") if isinstance(v, dict) else str(v) for v in variants], weights=weights)[0]
        assignment = ABTestAssignment(user_id=current_user.id, test_id=test.id, variant=chosen)
        session.add(assignment)
        await session.flush()
    session.add(ABTestEvent(assignment_id=assignment.id, event_name=event_name, value=value, metadata_json=metadata or {}))
    await session.commit()
    return {"variant": assignment.variant}


# ===== Ad =====
@router.get("/ads")
async def get_ads(region: str = None, age: int = 25, gender: str = None, session: AsyncSession = Depends(get_session)):
    now = datetime.utcnow()
    r = await session.execute(select(AdCampaign).where(AdCampaign.is_active == True, AdCampaign.starts_at <= now, (AdCampaign.ends_at.is_(None) | (AdCampaign.ends_at >= now)), AdCampaign.target_age_min <= age, AdCampaign.target_age_max >= age))
    campaigns = r.scalars().all()
    if region:
        campaigns = [c for c in campaigns if not c.target_regions or region in c.target_regions]
    if gender:
        campaigns = [c for c in campaigns if not c.target_genders or gender in c.target_genders]
    return [{"id": c.id, "name": c.name, "advertiser": c.advertiser, "type": c.type, "image_url": c.image_url, "target_url": c.target_url} for c in campaigns[:5]]


@router.post("/ads/{ad_id}/click")
async def click_ad(ad_id: int, session: AsyncSession = Depends(get_session)):
    a = await session.get(AdCampaign, ad_id)
    if a:
        a.clicks = (a.clicks or 0) + 1
        await session.commit()
    return {"ok": True}


# ===== Subscriptions =====
@router.get("/subscriptions")
async def list_subscriptions(session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.is_active == True).order_by(SubscriptionPlan.tier))
    return [{"id": s.id, "code": s.code, "name": s.name, "tier": s.tier, "price_stars": s.price_stars, "price_usd": s.price_usd, "duration_days": s.duration_days, "features": s.features, "boost_count": s.boost_count, "superlikes_per_day": s.superlikes_per_day, "is_vip": s.is_vip} for s in r.scalars().all()]


@router.post("/subscriptions/{sub_id}/purchase")
async def purchase_subscription(sub_id: int, telegram_payment_charge_id: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from app.services.premium import PremiumService
    from datetime import timedelta
    sub = await session.get(SubscriptionPlan, sub_id)
    if not sub:
        raise HTTPException(404)
    result = await PremiumService.verify_and_activate(session, current_user.id, sub.code, sub.duration_days, sub.price_stars, telegram_payment_charge_id)
    return result
