"""Dependency Injection — auth, admin, current user."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.security import decode_token
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    if not creds:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token topilmadi")

    try:
        payload = decode_token(creds.credentials)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))

    user_id = int(payload.get("sub", 0))
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Yaroqsiz token")

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Foydalanuvchi topilmadi")
    if user.is_banned:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Akkaunt bloklangan")
    if user.is_suspended and user.suspended_until and user.suspended_until > datetime.utcnow():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Akkaunt vaqtincha to'xtatilgan")

    # Oxirgi faollikni yangilash (har 5 daqiqada bir marta)
    return user


async def get_optional_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User | None:
    if not creds:
        return None
    try:
        return await get_current_user(creds, db)
    except HTTPException:
        return None


async def get_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat adminlar uchun")
    return user


async def get_premium_user(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    from app.services.premium_service import PremiumService
    if not await PremiumService.is_premium(db, user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Premium talab qilinadi")
    return user


# CSRF himoyasi (state-changing requests uchun)
async def verify_csrf(
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    csrf_cookie: Annotated[str | None, Header(alias="X-CSRF-Cookie")] = None,
):
    if not x_csrf_token or not csrf_cookie:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "CSRF token yo'q")
    if x_csrf_token != csrf_cookie:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "CSRF token mos kelmadi")
    return True
