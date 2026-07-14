"""Users router — profil, sozlamalar, lokatsiya."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import User, Profile
from app.schemas.user import ProfileUpdate, ProfileMe, LocationUpdate, BlockRequest
from app.services.user_service import UserService
from app.services.safety_service import SafetyService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ProfileMe)
async def get_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """O'z profilingiz to'liq ma'lumotlari."""
    res = await db.execute(
        select(User).options(selectinload(User.profile), selectinload(User.premium))
        .where(User.id == user.id)
    )
    me = res.scalar_one()
    profile = me.profile
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profil topilmadi")

    return ProfileMe(
        public_id=me.public_id,
        user_id=me.id,
        telegram_id=me.telegram_id,
        telegram_first_name=me.telegram_first_name,
        telegram_photo_url=me.telegram_photo_url,
        is_telegram_premium=me.is_telegram_premium,
        nickname=profile.nickname,
        age=profile.age(),
        gender=profile.gender,
        looking_for=profile.looking_for,
        region=profile.region,
        city=profile.city,
        interests=profile.interests or [],
        avatar_url=profile.avatar_url,
        photos=profile.photos or [],
        height_cm=profile.height_cm,
        occupation=profile.occupation,
        education=profile.education,
        languages=profile.languages or [],
        bio=profile.bio,
        is_online=me.is_online,
        last_seen=me.last_seen,
        is_verified=profile.is_verified,
        is_premium=me.premium.is_active if me.premium else False,
        is_boosted=profile.is_boosted,
        min_age_preference=profile.min_age_preference,
        max_age_preference=profile.max_age_preference,
        max_distance_km=profile.max_distance_km,
        show_only_online=profile.show_only_online,
        show_only_in_region=profile.show_only_in_region,
        profile_views=profile.profile_views,
        likes_received=profile.likes_received,
        likes_sent=profile.likes_sent,
        match_count=profile.match_count,
        is_banned=me.is_banned,
        is_suspended=me.is_suspended,
        role=me.role,
        preferred_language=me.preferred_language,
        theme=me.theme,
        created_at=me.created_at,
        updated_at=me.updated_at,
    )


@router.patch("/me")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """O'z profilini yangilash."""
    profile = await UserService.update_profile(db, user, data)
    return {
        "success": True,
        "is_complete": profile.is_complete,
        "profile": {
            "nickname": profile.nickname,
            "bio": profile.bio,
            "age": profile.age(),
        },
    }


@router.post("/me/location")
async def update_location(
    data: LocationUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Lokatsiyani yangilash."""
    await UserService.update_location(db, user, data.latitude, data.longitude)
    return {"success": True}


@router.post("/me/language")
async def set_language(
    language: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await UserService.set_preferred_language(db, user, language)
    return {"success": True, "language": user.preferred_language}


@router.post("/me/theme")
async def set_theme(
    theme: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await UserService.set_theme(db, user, theme)
    return {"success": True, "theme": user.theme}


@router.get("/{public_id}")
async def get_user_by_public_id(
    public_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Public_id orqali boshqa foydalanuvchini ko'rish (anonim)."""
    res = await db.execute(
        select(User).options(selectinload(User.profile), selectinload(User.premium))
        .where(User.public_id == public_id)
    )
    target = res.scalar_one_or_none()
    if not target or target.is_banned:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foydalanuvchi topilmadi")

    profile = target.profile
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profil topilmadi")

    return {
        "public_id": target.public_id,
        "nickname": profile.nickname,
        "age": profile.age(),
        "gender": profile.gender,
        "region": profile.region,
        "city": profile.city,
        "bio": profile.bio,
        "interests": profile.interests or [],
        "photos": profile.photos or [],
        "avatar_url": profile.avatar_url,
        "is_online": target.is_online,
        "last_seen": target.last_seen,
        "is_verified": profile.is_verified,
        "is_premium": target.premium.is_active if target.premium else False,
    }


@router.post("/block")
async def block_user(
    request: BlockRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await SafetyService.block_user(db, user, request)
    return {"success": True, "message": "Foydalanuvchi bloklandi"}


@router.delete("/block/{user_id}")
async def unblock_user(
    user_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    success = await SafetyService.unblock_user(db, user, user_id)
    return {"success": success, "message": "Blokdan chiqarildi" if success else "Blok topilmadi"}


@router.get("/blocks")
async def get_blocked_list(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    blocked = await SafetyService.get_blocked_list(db, user)
    return {"blocked_ids": blocked, "total": len(blocked)}
