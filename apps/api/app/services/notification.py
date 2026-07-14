"""Notification service"""
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.models.user import User
from app.core.redis import redis_client
import json


class NotificationService:
    @staticmethod
    async def create(session, user_id, type_, title, body, data=None):
        n = Notification(user_id=user_id, type=type_, title=title, body=body, data=data or {})
        session.add(n)
        await session.commit()
        await session.refresh(n)
        await redis_client.publish(f"user:{user_id}", json.dumps({"type": "notification", "data": {"id": n.id, "type": n.type, "title": n.title, "body": n.body, "created_at": n.created_at.isoformat()}}, default=str))
        return n

    @staticmethod
    async def send_match_notification(session, user_id, other_user_id):
        me = await session.get(User, user_id)
        other = await session.get(User, other_user_id)
        if not me or not other:
            return
        await NotificationService.create(session, user_id, type_="new_match", title="Yangi match! 💕", body=f"Siz va {other.nickname} bir-biringizga yoqdingiz!", data={"other_user_id": other_user_id, "other_nickname": other.nickname})

    @staticmethod
    async def mark_all_read(session, user_id):
        await session.execute(update(Notification).where(Notification.user_id == user_id, Notification.is_read == False).values(is_read=True, read_at=datetime.utcnow()))
        await session.commit()

    @staticmethod
    async def list_notifications(session, user_id, limit=50):
        result = await session.execute(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(limit))
        notifs = result.scalars().all()
        unread = sum(1 for n in notifs if not n.is_read)
        return {"notifications": [{"id": n.id, "type": n.type, "title": n.title, "body": n.body, "data": n.data, "is_read": n.is_read, "created_at": n.created_at} for n in notifs], "unread_count": unread}
