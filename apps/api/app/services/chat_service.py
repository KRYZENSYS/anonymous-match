"""Chat service — xabarlar, real-time."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis_client import get_redis, chat_channel
from app.models import User, Chat, Message, Block, Match
from app.schemas.chat import MessageCreate, MessagePublic, MessageUpdate

logger = logging.getLogger(__name__)


class ChatService:
    """Chat va xabarlar servisi."""

    @staticmethod
    async def get_user_chats(db: AsyncSession, user: User) -> list[dict]:
        res = await db.execute(
            select(Chat)
            .where(
                or_(Chat.user1_id == user.id, Chat.user2_id == user.id),
                Chat.is_active == True,
            )
            .order_by(Chat.last_message_at.desc().nulls_last())
            .options(selectinload(Chat.user1), selectinload(Chat.user2))
        )
        chats = res.scalars().all()

        result = []
        for chat in chats:
            other_id = chat.get_other_user_id(user.id)
            other = chat.user1 if other_id == chat.user1_id else chat.user2
            if not other.profile:
                continue
            result.append({
                "id": chat.id,
                "other_user_public_id": other.public_id,
                "other_user_nickname": other.profile.nickname,
                "other_user_avatar": other.profile.avatar_url,
                "last_message_at": chat.last_message_at,
                "last_message_preview": chat.last_message_preview,
                "unread_count": chat.get_unread_for(user.id),
                "is_match": chat.type == "match",
                "is_online": other.is_online,
                "created_at": chat.created_at,
            })
        return result

    @staticmethod
    async def get_or_create_chat(
        db: AsyncSession, user: User, other_user_id: int
    ) -> Chat:
        if other_user_id == user.id:
            raise ValueError("O'zingiz bilan chat qilib bo'lmaydi")
        u1, u2 = sorted([user.id, other_user_id])
        res = await db.execute(
            select(Chat).where(Chat.user1_id == u1, Chat.user2_id == u2)
        )
        chat = res.scalar_one_or_none()
        if not chat:
            chat = Chat(user1_id=u1, user2_id=u2, type="direct")
            db.add(chat)
            await db.flush()
        return chat

    @staticmethod
    async def send_message(
        db: AsyncSession,
        user: User,
        chat_id: int,
        data: MessageCreate,
    ) -> Message:
        res = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = res.scalar_one_or_none()
        if not chat:
            raise ValueError("Chat topilmadi")
        if user.id not in (chat.user1_id, chat.user2_id):
            raise PermissionError("Bu chat sizga tegishli emas")
        if chat.is_blocked:
            raise PermissionError("Chat bloklangan")

        other_id = chat.get_other_user_id(user.id)
        block_check = await db.execute(
            select(Block).where(
                or_(
                    and_(Block.blocker_id == user.id, Block.blocked_id == other_id),
                    and_(Block.blocker_id == other_id, Block.blocked_id == user.id),
                )
            )
        )
        if block_check.scalar_one_or_none():
            raise PermissionError("Bloklangan foydalanuvchi")

        if data.type == "text" and not data.content:
            raise ValueError("Matn bush")
        if data.type in ("image", "video", "voice", "sticker", "gif") and not data.media_id:
            raise ValueError("Media ID kerak")

        msg = Message(
            chat_id=chat_id,
            sender_id=user.id,
            type=data.type,
            content=data.content,
            media_id=data.media_id,
            reply_to_id=data.reply_to_id,
            extra=data.extra,
        )
        db.add(msg)
        await db.flush()

        chat.last_message_at = msg.created_at
        preview = data.content if data.type == "text" else f"[{data.type}]"
        chat.last_message_preview = preview[:255] if preview else None

        if user.id == chat.user1_id:
            chat.user2_unread += 1
        else:
            chat.user1_unread += 1

        if chat.match_id:
            res = await db.execute(select(Match).where(Match.id == chat.match_id))
            match = res.scalar_one_or_none()
            if match and not match.first_message_sent:
                match.first_message_sent = True

        await db.flush()

        # WebSocket orqali
        redis = get_redis()
        event = {
            "type": "message",
            "data": {
                "id": msg.id,
                "chat_id": chat_id,
                "sender_id": user.id,
                "sender_public_id": user.public_id,
                "type": msg.type,
                "content": msg.content,
                "media_id": msg.media_id,
                "reply_to_id": msg.reply_to_id,
                "created_at": msg.created_at.isoformat(),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await redis.publish(chat_channel(chat_id), json.dumps(event, default=str))

        # Notification
        try:
            from app.services.notification_service import NotificationService
            await NotificationService.create(
                db=db,
                user_id=other_id,
                type="new_message",
                title=other.profile.nickname if other.profile else "Yangi xabar",
                body=preview or "Yangi xabar",
                icon="💬",
                data={"chat_id": chat_id, "message_id": msg.id},
                related_user_id=user.id,
                related_chat_id=chat_id,
            )
        except Exception as e:
            logger.warning(f"Notification failed: {e}")

        return msg

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        user: User,
        chat_id: int,
        limit: int = 50,
        before: Optional[datetime] = None,
    ) -> list[MessagePublic]:
        res = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = res.scalar_one_or_none()
        if not chat or user.id not in (chat.user1_id, chat.user2_id):
            raise PermissionError("Bu chat sizga tegishli emas")

        q = select(Message).where(Message.chat_id == chat_id, Message.is_deleted == False)
        if before:
            q = q.where(Message.created_at < before)
        q = q.order_by(Message.created_at.desc()).limit(limit)

        res = await db.execute(q)
        messages = list(res.scalars().all())
        messages.reverse()

        return [
            MessagePublic(
                id=m.id,
                chat_id=m.chat_id,
                sender_id=m.sender_id,
                sender_public_id=m.sender.public_id if m.sender else "",
                type=m.type,
                content=m.content,
                media=None,
                reply_to=None,
                is_edited=m.is_edited,
                is_deleted=m.is_deleted,
                is_mine=m.sender_id == user.id,
                read_at=m.read_at,
                delivered_at=m.delivered_at,
                created_at=m.created_at,
            )
            for m in messages
        ]

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        user: User,
        chat_id: int,
        message_ids: list[int] = None,
    ) -> int:
        now = datetime.utcnow()
        q = (
            update(Message)
            .where(
                Message.chat_id == chat_id,
                Message.sender_id != user.id,
                Message.read_at.is_(None),
            )
            .values(read_at=now, delivered_at=now)
        )
        if message_ids:
            q = q.where(Message.id.in_(message_ids))
        result = await db.execute(q)
        await db.flush()

        res = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = res.scalar_one_or_none()
        if chat:
            if user.id == chat.user1_id:
                chat.user1_unread = 0
            else:
                chat.user2_unread = 0
            await db.flush()
        return result.rowcount or 0

    @staticmethod
    async def delete_message(
        db: AsyncSession,
        user: User,
        message_id: int,
        for_everyone: bool = False,
    ) -> bool:
        res = await db.execute(select(Message).where(Message.id == message_id))
        msg = res.scalar_one_or_none()
        if not msg:
            return False
        if msg.sender_id != user.id and not user.is_admin:
            raise PermissionError("Bu xabarni o'chirish huquqi yo'q")
        if for_everyone and msg.sender_id == user.id:
            msg.deleted_for_everyone = True
            msg.is_deleted = True
            msg.content = None
        else:
            msg.is_deleted = True
        msg.deleted_by = user.id
        await db.flush()
        return True

    @staticmethod
    async def edit_message(
        db: AsyncSession,
        user: User,
        message_id: int,
        data: MessageUpdate,
    ) -> Message:
        res = await db.execute(select(Message).where(Message.id == message_id))
        msg = res.scalar_one_or_none()
        if not msg:
            raise ValueError("Xabar topilmadi")
        if msg.sender_id != user.id:
            raise PermissionError("Bu xabarni tahrirlash huquqi yo'q")
        if (datetime.utcnow() - msg.created_at).total_seconds() > 900:
            raise ValueError("15 daqiqadan keyin tahrirlab bo'lmaydi")
        msg.content = data.content
        msg.is_edited = True
        await db.flush()
        return msg

    @staticmethod
    async def set_typing(db: AsyncSession, user: User, chat_id: int, is_typing: bool):
        redis = get_redis()
        event = {
            "type": "typing",
            "data": {
                "chat_id": chat_id,
                "user_id": user.id,
                "public_id": user.public_id,
                "is_typing": is_typing,
            },
        }
        await redis.publish(chat_channel(chat_id), json.dumps(event))
