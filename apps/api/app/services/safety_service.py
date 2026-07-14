"""Safety service — bloklash, report."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Block, Report, Log, Chat, Match
from app.schemas.user import BlockRequest, ReportRequest

logger = logging.getLogger(__name__)


class SafetyService:
    """Foydalanuvchi xavfsizligi."""

    @staticmethod
    async def block_user(
        db: AsyncSession, user: User, request: BlockRequest
    ) -> Block:
        if request.blocked_id == user.id:
            raise ValueError("O'zingizni bloklay olmaysiz")

        # Allaqachon bloklanganmi
        res = await db.execute(
            select(Block).where(
                Block.blocker_id == user.id,
                Block.blocked_id == request.blocked_id,
            )
        )
        if res.scalar_one_or_none():
            raise ValueError("Allaqachon bloklangansiz")

        block = Block(
            blocker_id=user.id,
            blocked_id=request.blocked_id,
            reason=request.reason,
        )
        db.add(block)

        # Chatlarni ham bloklash
        other = request.blocked_id
        u1, u2 = sorted([user.id, other])
        res2 = await db.execute(
            select(Chat).where(Chat.user1_id == u1, Chat.user2_id == u2)
        )
        chat = res2.scalar_one_or_none()
        if chat:
            chat.is_blocked = True
            chat.blocked_by = user.id

        db.add(Log(
            user_id=user.id,
            level="warning",
            category="security",
            action="user_blocked",
            message=f"Foydalanuvchi bloklandi: {other}",
            details={"blocked_id": other, "reason": request.reason},
        ))

        await db.flush()
        return block

    @staticmethod
    async def unblock_user(
        db: AsyncSession, user: User, blocked_id: int
    ) -> bool:
        res = await db.execute(
            select(Block).where(
                Block.blocker_id == user.id,
                Block.blocked_id == blocked_id,
            )
        )
        block = res.scalar_one_or_none()
        if not block:
            return False
        await db.delete(block)

        # Chat blokni ochish
        u1, u2 = sorted([user.id, blocked_id])
        res2 = await db.execute(
            select(Chat).where(Chat.user1_id == u1, Chat.user2_id == u2)
        )
        chat = res2.scalar_one_or_none()
        if chat and chat.blocked_by == user.id:
            chat.is_blocked = False
            chat.blocked_by = None

        await db.flush()
        return True

    @staticmethod
    async def is_blocked(
        db: AsyncSession, user_id: int, other_id: int
    ) -> bool:
        res = await db.execute(
            select(Block).where(
                or_(
                    and_(Block.blocker_id == user_id, Block.blocked_id == other_id),
                    and_(Block.blocker_id == other_id, Block.blocked_id == user_id),
                )
            )
        )
        return res.scalar_one_or_none() is not None

    @staticmethod
    async def get_blocked_list(db: AsyncSession, user: User) -> list[int]:
        res = await db.execute(
            select(Block.blocked_id).where(Block.blocker_id == user.id)
        )
        return [r[0] for r in res.all()]

    @staticmethod
    async def report_user(
        db: AsyncSession, user: User, request: ReportRequest
    ) -> Report:
        if request.reported_id == user.id:
            raise ValueError("O'zingizni report qila olmaysiz")

        # 24 soat ichida bitta odamga bitta report
        res = await db.execute(
            select(Report).where(
                Report.reporter_id == user.id,
                Report.reported_id == request.reported_id,
                Report.created_at > datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            )
        )
        if res.scalar_one_or_none():
            raise ValueError("Bugun allaqachon report qilgansiz")

        report = Report(
            reporter_id=user.id,
            reported_id=request.reported_id,
            reason=request.reason,
            description=request.description,
            evidence_chat_id=request.chat_id,
            evidence_message_id=request.message_id,
            evidence_media_id=request.media_id,
        )
        db.add(report)

        db.add(Log(
            user_id=user.id,
            level="warning",
            category="security",
            action="user_reported",
            message=f"Foydalanuvchi report qilindi: {request.reported_id}",
            details={"reported_id": request.reported_id, "reason": request.reason},
        ))

        await db.flush()
        return report

    @staticmethod
    async def get_my_reports(db: AsyncSession, user: User) -> list[Report]:
        res = await db.execute(
            select(Report)
            .where(Report.reporter_id == user.id)
            .order_by(Report.created_at.desc())
            .limit(100)
        )
        return list(res.scalars().all())
