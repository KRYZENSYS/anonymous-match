"""Notification service - Telegram, FCM, in-app"""
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from app.models.notification import Notification
from app.models.user import User
from app.core.config import settings
from app.core.redis import redis_client

try:
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False

try:
    import firebase_admin
    from firebase_admin import messaging
    FCM_AVAILABLE = True
except ImportError:
    FCM_AVAILABLE = False


class NotificationService:
    """Send push, telegram, in-app notifications"""

    _bot = None

    @classmethod
    def get_bot(cls):
        if cls._bot is None and TELEGRAM_BOT_AVAILABLE and settings.BOT_TOKEN:
            cls._bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
        return cls._bot

    @staticmethod
    async def send(session: AsyncSession, user_id: int, type: str, title: str, body: str, data: dict = None, image_url: str = None):
        """Send notification (in-app + telegram push)"""
        # 1. Save in-app
        n = Notification(
            user_id=user_id, type=type, title=title, body=body,
            data=json.dumps(data or {}), image_url=image_url,
        )
        session.add(n)
        await session.commit()
        # 2. Push to Redis (for real-time in-app)
        payload = {"id": n.id, "type": type, "title": title, "body": body, "data": data, "created_at": str(n.created_at)}
        try:
            await redis_client.publish(f"user:{user_id}", json.dumps({"type": "notification", "data": payload}, default=str))
        except Exception:
            pass
        # 3. Telegram push
        user = await session.get(User, user_id)
        if user and user.telegram_id:
            await NotificationService._send_telegram(user.telegram_id, title, body, data)
        # 4. FCM
        if user and user.fcm_token:
            await NotificationService._send_fcm(user.fcm_token, title, body, data)
        return n

    @staticmethod
    async def _send_telegram(telegram_id: int, title: str, body: str, data: dict = None):
        bot = NotificationService.get_bot()
        if not bot:
            return
        try:
            text = f"<b>{title}</b>\n\n{body}"
            await bot.send_message(chat_id=telegram_id, text=text)
        except Exception:
            pass

    @staticmethod
    async def _send_fcm(token: str, title: str, body: str, data: dict = None):
        if not FCM_AVAILABLE:
            return
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                token=token,
            )
            messaging.send(message)
        except Exception:
            pass

    @staticmethod
    async def notify_new_match(session: AsyncSession, user_id: int, match_user: User):
        await NotificationService.send(
            session, user_id, "new_match",
            "Yangi match! 💕",
            f"Siz {match_user.nickname or 'foydalanuvchi'} bilan match bo'ldingiz!",
            {"match_id": match_user.id, "user_id": match_user.id},
        )

    @staticmethod
    async def notify_new_message(session: AsyncSession, recipient_id: int, sender: User, preview: str, chat_id: int):
        await NotificationService.send(
            session, recipient_id, "new_message",
            f"💬 {sender.nickname or 'Yangi xabar'}",
            preview[:200],
            {"chat_id": chat_id, "sender_id": sender.id},
        )

    @staticmethod
    async def notify_like(session: AsyncSession, recipient_id: int, liker: User):
        await NotificationService.send(
            session, recipient_id, "new_like",
            "Kimdir sizni yoqtirdi! ❤️",
            f"{liker.nickname or 'Foydalanuvchi'} sizni yoqtirdi",
            {"user_id": liker.id},
        )

    @staticmethod
    async def notify_superlike(session: AsyncSession, recipient_id: int, liker: User):
        await NotificationService.send(
            session, recipient_id, "superlike",
            "⭐️ Super Like!",
            f"{liker.nickname or 'Foydalanuvchi'} sizga Super Like berdi!",
            {"user_id": liker.id},
        )

    @staticmethod
    async def notify_achievement(session: AsyncSession, user_id: int, name: str, icon: str):
        await NotificationService.send(
            session, user_id, "achievement",
            f"{icon} Yangi yutuq!",
            f"'{name}' yutuqini qo'lga kiritdingiz!",
        )

    @staticmethod
    async def notify_event(session: AsyncSession, user_id: int, event_title: str):
        await NotificationService.send(
            session, user_id, "event",
            "🎉 Yangi tadbir!",
            event_title,
        )

    @staticmethod
    async def mark_read(session: AsyncSession, user_id: int, notification_ids: List[int] = None):
        """Mark notifications as read"""
        if notification_ids:
            for nid in notification_ids:
                n = await session.get(Notification, nid)
                if n and n.user_id == user_id:
                    n.is_read = True
        else:
            # Mark all as read
            r = await session.execute(select(Notification).where(Notification.user_id == user_id, Notification.is_read == False))
            for n in r.scalars().all():
                n.is_read = True
        await session.commit()

    @staticmethod
    async def get_unread_count(session: AsyncSession, user_id: int) -> int:
        r = await session.execute(select(Notification).where(Notification.user_id == user_id, Notification.is_read == False))
        return len(r.scalars().all())

    @staticmethod
    async def get_notifications(session: AsyncSession, user_id: int, limit: int = 50):
        r = await session.execute(select(Notification).where(Notification.user_id == user_id).order_by(desc(Notification.created_at)).limit(limit))
        return r.scalars().all()
