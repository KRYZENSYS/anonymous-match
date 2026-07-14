"""Notification service — bildirishnomalar yuborish."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_redis, notify_channel
from app.models import Notification, User, Log

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        type: str,
        title: str,
        body: str,
        icon: Optional[str] = None,
        data: Optional[dict] = None,
        related_user_id: Optional[int] = None,
        related_chat_id: Optional[int] = None,
        related_match_id: Optional[int] = None,
        send_push: bool = True,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            icon=icon,
            data=data,
            related_user_id=related_user_id,
            related_chat_id=related_chat_id,
            related_match_id=related_match_id,
        )
        db.add(notif)
        await db.flush()

        # Redis pubsub
        redis = get_redis()
        event = {
            "type": "notification",
            "data": {
                "id": notif.id,
                "type": type,
                "title": title,
                "body": body,
                "icon": icon,
                "data": data,
                "related_user_id": related_user_id,
                "related_chat_id": related_chat_id,
                "related_match_id": related_match_id,
                "created_at": notif.created_at.isoformat(),
            },
        }
        await redis.publish(notify_channel(user_id), json.dumps(event, default=str))

        return notif

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession, user: User, limit: int = 50, offset: int = 0,
    ) -> list[Notification]:
        res = await db.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .limit(limit).offset(offset)
        )
        return list(res.scalars().all())

    @staticmethod
    async def get_unread_count(db: AsyncSession, user: User) -> int:
        res = await db.execute(
            select(Notification).where(
                Notification.user_id == user.id,
                Notification.is_read == False,
            )
        )
        return len(list(res.scalars().all()))

    @staticmethod
    async def mark_read(db: AsyncSession, user: User, notif_ids: list[int] = None) -> int:
        q = (
            update(Notification)
            .where(Notification.user_id == user.id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        if notif_ids:
            q = q.where(Notification.id.in_(notif_ids))
        result = await db.execute(q)
        await db.flush()
        return result.rowcount or 0

    @staticmethod
    async def mark_all_read(db: AsyncSession, user: User) -> int:
        return await NotificationService.mark_read(db, user)
