"""Admin router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_admin_user
from app.models import User, Report
from app.schemas.notification import (
    AdminStats, BanUserRequest, SuspendUserRequest, BroadcastRequest,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_admin_user)])


@router.get("/stats", response_model=AdminStats)
async def get_stats(db: AsyncSession = Depends(get_session)):
    return AdminStats(**await AdminService.get_stats(db))


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_session),
    search: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    if search:
        like = f"%{search}%"
        q = q.where(or_(
            User.telegram_username.ilike(like),
            User.public_id.ilike(like),
        ))
    res = await db.execute(q)
    users = res.scalars().all()
    return {
        "users": [
            {
                "id": u.id,
                "public_id": u.public_id,
                "username": u.telegram_username,
                "first_name": u.telegram_first_name,
                "is_admin": u.is_admin,
                "is_banned": u.is_banned,
                "is_online": u.is_online,
                "is_premium": u.premium.is_active if u.premium else False,
                "created_at": u.created_at,
                "last_seen": u.last_seen,
            }
            for u in users
        ],
        "total": len(users),
    }


@router.post("/ban")
async def ban_user(
    request: BanUserRequest,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        await AdminService.ban_user(db, admin, request.user_id, request.reason, request.duration_days)
        return {"success": True}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/unban")
async def unban_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        await AdminService.unban_user(db, admin, user_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/suspend")
async def suspend_user(
    request: SuspendUserRequest,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        await AdminService.suspend_user(db, admin, request.user_id, request.reason, request.until)
        return {"success": True}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/grant-premium")
async def grant_premium(
    user_id: int,
    days: int = 30,
    tier: str = "plus",
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        await AdminService.grant_premium(db, admin, user_id, days, tier)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.get("/reports/pending")
async def pending_reports(
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    reports = await AdminService.get_pending_reports(db, limit, offset)
    return {
        "reports": [
            {
                "id": r.id,
                "reporter_id": r.reporter_id,
                "reported_id": r.reported_id,
                "reason": r.reason,
                "description": r.description,
                "evidence_chat_id": r.evidence_chat_id,
                "evidence_message_id": r.evidence_message_id,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in reports
        ],
        "total": len(reports),
    }


@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    action: str,
    note: str = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        await AdminService.resolve_report(db, admin, report_id, action, note)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/broadcast")
async def broadcast(
    request: BroadcastRequest,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_session),
):
    count = await AdminService.broadcast(
        db, admin, request.title, request.body,
        request.target, request.image_url,
    )
    return {"success": True, "sent_to": count}
