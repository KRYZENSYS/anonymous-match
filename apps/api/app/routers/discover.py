"""Discover router — swipe, profiles, match."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import User, Profile
from app.schemas.match import SwipeRequest, SwipeResponse, MatchListResponse, MatchPublic
from app.schemas.user import ProfilePublic, DiscoverFilters
from app.services.match_service import MatchService

router = APIRouter(prefix="/discover", tags=["Discover"])


@router.get("")
async def discover(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    min_age: int = Query(18, ge=18, le=99),
    max_age: int = Query(99, ge=18, le=99),
    gender: str = Query("any"),
    region: str = Query(None),
    city: str = Query(None),
    online_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=50),
):
    """Swipe uchun profillar."""
    profiles = await MatchService.get_discover_profiles(
        db, user,
        min_age=min_age,
        max_age=max_age,
        gender=gender,
        region=region,
        city=city,
        online_only=online_only,
        limit=limit,
    )

    result = []
    for p in profiles:
        if not p.user:
            continue
        # Distance hisoblash
        distance = None
        if user.profile and user.profile.latitude and p.latitude:
            from math import radians, sin, cos, sqrt, atan2
            R = 6371.0
            lat1, lon1 = radians(user.profile.latitude), radians(user.profile.longitude)
            lat2, lon2 = radians(p.latitude), radians(p.longitude)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = round(R * c, 1)

        is_prem = False
        if hasattr(p.user, "premium") and p.user.premium:
            is_prem = p.user.premium.is_active

        result.append({
            "public_id": p.user.public_id,
            "nickname": p.nickname,
            "age": p.age(),
            "gender": p.gender,
            "region": p.region,
            "city": p.city,
            "bio": p.bio,
            "interests": p.interests or [],
            "photos": p.photos or [],
            "avatar_url": p.avatar_url,
            "is_online": p.user.is_online,
            "is_verified": p.is_verified,
            "is_premium": is_prem,
            "is_boosted": p.is_boosted,
            "distance_km": distance,
        })

    return {"profiles": result, "total": len(result)}


@router.post("/swipe", response_model=SwipeResponse)
async def swipe(
    request: SwipeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Like / Pass / SuperLike."""
    try:
        return await MatchService.swipe(db, user, request)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.get("/matches", response_model=MatchListResponse)
async def get_my_matches(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Mening matchlarim."""
    matches = await MatchService.get_my_matches(db, user)
    return MatchListResponse(matches=matches, total=len(matches))


@router.delete("/matches/{match_id}")
async def unmatch(
    match_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Matchni bekor qilish."""
    from sqlalchemy import select, or_
    from app.models import Match, Chat
    res = await db.execute(
        select(Match).where(
            Match.id == match_id,
            or_(Match.user1_id == user.id, Match.user2_id == user.id),
        )
    )
    match = res.scalar_one_or_none()
    if not match:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Match topilmadi")

    match.is_unmatched = True
    match.unmatched_by = user.id
    match.is_active = False

    if match.chat_id:
        cres = await db.execute(select(Chat).where(Chat.id == match.chat_id))
        chat = cres.scalar_one_or_none()
        if chat:
            chat.is_active = False

    return {"success": True, "message": "Match bekor qilindi"}
