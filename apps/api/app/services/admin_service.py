"""Admin service — admin panel uchun."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Profile, Match, Message, Report, Premium, Subscription, Log, Notification, Chat

logger = logging.getLogger(__name__)


class AdminService:
    """Admin panel servisi."""

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        """Umumiy statistika."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)

        total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
        active_today = (await db.execute(
            select(func.count(User.id)).where(User.last_active_at >= today_start)
        )).scalar() or 0
        active_week = (await db.execute(
            select(func.count(User.id)).where(User.last_active_at >= week_start)
        )).scalar() or 0
        new_today = (await db.execute(
            select(func.count(User.id)).where(User.created_at >= today_start)
        )).scalar() or 0
        total_matches = (await db.execute(select(func.count(Match.id)))).scalar() or 0
        total_messages = (await db.execute(select(func.count(Message.id)))).scalar() or 0
        pending_reports = (await db.execute(
            select(func.count(Report.id)).where(Report.status == "pending")
        )).scalar() or 0
        premium_users = (await db.execute(
            select(func.count(Premium.id)).where(Premium.is_active == True)
        )).scalar() or 0
        revenue = (await db.execute(
            select(func.coalesce(func.sum(Subscription.price_stars), 0))
            .where(Subscription.status == "active")
        )).scalar() or 0
        online_now = (await db.execute(
            select(func.count(User.id)).where(User.is_online == True)
        )).scalar() or 0

        return {
            "total_users": total_users,
            "active_users_today": active_today,
            "active_users_week": active_week,
            "new_users_today": new_today,
            "total_matches": total_matches,
            "total_messages": total_messages,
            "total_reports_pending": pending_reports,
            "total_premium_users": premium_users,
            "revenue_total_stars": int(revenue),
            "online_now": online_now,
        }

    @staticmethod
    async def ban_user(
        db: AsyncSession, admin: User, user_id: int, reason: str,
        duration_days: Optional[int] = None
    ) -> bool:
        res = await db.execute(select(User).where(User.id == user_id))
        target = res.scalar_one_or_none()
        if not target:
            raise ValueError("Foydalanuvchi topilmadi")
        if target.is_admin:
            raise PermissionError("Adminni bloklab bo'lmaydi")

        target.is_banned = True
        target.ban_reason = reason
        target.suspended_until = None
        target.is_suspended = False
        target.is_online = False

        db.add(Log(
            user_id=admin.id,
            level="audit",
            category="admin",
            action="user_banned",
            message=f"User banned: {user_id}",
            details={"target_id": user_id, "reason": reason, "duration_days": duration_days},
        ))

        await db.flush()
        return True

    @staticmethod
    async def suspend_user(
        db: AsyncSession, admin: User, user_id: int, reason: str, until: datetime
    ) -> bool:
        res = await db.execute(select(User).where(User.id == user_id))
        target = res.scalar_one_or_none()
        if not target:
            raise ValueError("Foydalanuvchi topilmadi")
        if target.is_admin:
            raise PermissionError("Adminni to'xtatib bo'lmaydi")

        target.is_suspended = True
        target.suspended_until = until
        target.ban_reason = reason
        target.is_online = False

        db.add(Log(
            user_id=admin.id,
            level="audit",
            category="admin",
            action="user_suspended",
            message=f"User suspended: {user_id}",
            details={"target_id": user_id, "until": until.isoformat(), "reason": reason},
        ))

        await db.flush()
        return True

    @staticmethod
    async def unban_user(db: AsyncSession, admin: User, user_id: int) -> bool:
        res = await db.execute(select(User).where(User.id == user_id))
        target = res.scalar_one_or_none()
        if not target:
            raise ValueError("Foydalanuvchi topilmadi")

        target.is_banned = False
        target.is_suspended = False
        target.suspended_until = None
        target.ban_reason = None

        db.add(Log(
            user_id=admin.id,
            level="audit",
            category="admin",
            action="user_unbanned",
            message=f"User unbanned: {user_id}",
            details={"target_id": user_id},
        ))

        await db.flush()
        return True

    @staticmethod
    async def grant_premium(
        db: AsyncSession, admin: User, user_id: int, days: int, tier: str = "plus"
    ):
        from app.services.premium_service import PremiumService
        res = await db.execute(select(User).where(User.id == user_id))
        target = res.scalar_one_or_none()
        if not target:
            raise ValueError("Foydalanuvchi topilmadi")
        sub = await PremiumService.purchase(
            db, target, tier=tier, duration_days=days,
            price_stars=0, payment_id=f"admin_grant_{admin.id}"
        )
        db.add(Log(
            user_id=admin.id,
            level="audit",
            category="admin",
            action="premium_granted",
            message=f"Premium berildi: {user_id}",
            details={"target_id": user_id, "tier": tier, "days": days},
        ))
        return sub

    @staticmethod
    async def get_pending_reports(db: AsyncSession, limit: int = 50, offset: int = 0):
        res = await db.execute(
            select(Report)
            .where(Report.status == "pending")
            .order_by(Report.created_at.desc())
            .limit(limit).offset(offset)
        )
        return list(res.scalars().all())

    @staticmethod
    async def resolve_report(
        db: AsyncSession, admin: User, report_id: int,
        action: str, note: Optional[str] = None
    ):
        res = await db.execute(select(Report).where(Report.id == report_id))
        report = res.scalar_one_or_none()
        if not report:
            raise ValueError("Report topilmadi")

        report.status = "resolved"
        report.moderator_id = admin.id
        report.moderator_note = note
        report.action_taken = action
        report.resolved_at = datetime.utcnow()

        # Action ga qarab chora ko'rish
        if action == "banned":
            await AdminService.ban_user(db, admin, report.reported_id, note or "Report orqali")
        elif action == "warned":
            pass  # Warning notification
        elif action == "no_action":
            pass

        await db.flush()
        return report

    @staticmethod
    async def broadcast(
        db: AsyncSession, admin: User, title: str, body: str,
        target: str = "all", image_url: Optional[str] = None
    ) -> int:
        """Barcha foydalanuvchilarga notification yuborish."""
        q = select(User.id)
        if target == "premium":
            q = q.join(Premium, Premium.user_id == User.id).where(Premium.is_active == True)
        elif target == "online":
            q = q.where(User.is_online == True)
        elif target == "new_users":
            week_ago = datetime.utcnow() - timedelta(days=7)
            q = q.where(User.created_at >= week_ago)

        res = await db.execute(q)
        user_ids = [r[0] for r in res.all()]

        from app.services.notification_service import NotificationService
        for uid in user_ids:
            await NotificationService.create(
                db=db, user_id=uid, type="announcement",
                title=title, body=body, icon="📢",
                data={"admin_id": admin.id, "image_url": image_url}
            )

        db.add(Log(
            user_id=admin.id,
            level="audit",
            category="admin",
            action="broadcast",
            message=f"Broadcast: {title}",
            details={"target": target, "count": len(user_ids)},
        ))

        await db.flush()
        return len(user_ids)
