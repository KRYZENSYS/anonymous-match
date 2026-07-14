"""Notifications router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import User
from app.schemas.notification import NotificationListResponse, NotificationPublic
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    notifs = await NotificationService.get_user_notifications(db, user, limit, offset)
    unread = await NotificationService.get_unread_count(db, user)
    return NotificationListResponse(
        notifications=[
            NotificationPublic(
                id=n.id, type=n.type, title=n.title, body=n.body,
                icon=n.icon, data=n.data, is_read=n.is_read,
                created_at=n.created_at,
            ) for n in notifs
        ],
        unread_count=unread,
        total=len(notifs),
        has_more=len(notifs) == limit,
    )


@router.get("/unread-count")
async def unread_count(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    count = await NotificationService.get_unread_count(db, user)
    return {"unread_count": count}


@router.post("/read")
async def mark_read(
    notification_ids: list[int] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    count = await NotificationService.mark_read(db, user, notification_ids)
    return {"success": True, "marked_count": count}


@router.post("/read-all")
async def mark_all_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    count = await NotificationService.mark_all_read(db, user)
    return {"success": True, "marked_count": count}
