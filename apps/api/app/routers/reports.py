"""Reports router — foydalanuvchini report qilish."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import User
from app.schemas.user import ReportRequest
from app.services.safety_service import SafetyService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("")
async def create_report(
    request: ReportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        report = await SafetyService.report_user(db, user, request)
        return {
            "success": True,
            "report_id": report.id,
            "message": "Report qabul qilindi. Tez orada ko'rib chiqamiz.",
        }
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.get("/my")
async def my_reports(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    reports = await SafetyService.get_my_reports(db, user)
    return {
        "reports": [
            {
                "id": r.id,
                "reported_id": r.reported_id,
                "reason": r.reason,
                "status": r.status,
                "action_taken": r.action_taken,
                "created_at": r.created_at,
                "resolved_at": r.resolved_at,
            }
            for r in reports
        ],
        "total": len(reports),
    }
