"""Auth router — login, register, logout."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.security import validate_telegram_init_data
from app.models import User, Log
from app.schemas.auth import TelegramAuthRequest, AuthResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/telegram", response_model=AuthResponse)
async def telegram_login(
    request: TelegramAuthRequest,
    db: AsyncSession = Depends(get_session),
):
    """
    Telegram WebApp orqali login.
    initData validatsiyasidan keyin user yaratiladi yoki topiladi.
    """
    # InitData validatsiya
    telegram_data = validate_telegram_init_data(request.init_data)
    if not telegram_data:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Telegram initData noto'g'ri yoki eskirgan",
        )

    # User yaratish yoki olish
    user, is_new = await UserService.get_or_create_from_telegram(
        db, telegram_data, request.device_id, request.webapp_version
    )

    # Token
    token, expires_in = UserService.create_token(user)

    # Profile borligini tekshirish
    profile = await UserService.get_profile(db, user)

    return AuthResponse(
        access_token=token,
        expires_in=expires_in,
        user_id=user.id,
        public_id=user.public_id,
        is_new_user=is_new,
        is_profile_complete=profile.is_complete if profile else False,
        needs_profile_setup=is_new or not (profile and profile.is_complete),
    )


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Logout — foydalanuvchini offline qilish."""
    await UserService.set_online(db, user, False)
    db.add(Log(
        user_id=user.id,
        level="info",
        category="auth",
        action="logout",
        message="Foydalanuvchi tizimdan chiqdi",
    ))
    return {"success": True, "message": "Tizimdan chiqdingiz"}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    """Joriy foydalanuvchi ma'lumotlari."""
    return {
        "id": user.id,
        "public_id": user.public_id,
        "telegram_id": user.telegram_id,
        "is_admin": user.is_admin,
        "is_online": user.is_online,
        "preferred_language": user.preferred_language,
        "theme": user.theme,
        "is_telegram_premium": user.is_telegram_premium,
    }
