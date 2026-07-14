"""Chat service"""
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat, Message
from app.models.user import User
from app.core.redis import redis_client
import json


class ChatService:
    @staticmethod
    async def get_chats(session, user_id, limit=50):
        stmt = select(Chat, User).join(User, or_(and_(Chat.user1_id == user_id, User.id == Chat.user2_id), and_(Chat.user2_id == user_id, User.id == Chat.user1_id))).where(or_(Chat.user1_id == user_id, Chat.user2_id == user_id)).order_by(Chat.last_message_at.desc().nullslast()).limit(limit)
        result = await session.execute(stmt)
        rows = result.all()
        chats = []
        for chat, other in rows:
            last_msg_stmt = select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at.desc()).limit(1)
            last_msg = (await session.execute(last_msg_stmt)).scalar_one_or_none()
            unread_stmt = select(func.count(Message.id)).where(and_(Message.chat_id == chat.id, Message.sender_id != user_id, Message.read_at.is_(None)))
            unread = (await session.execute(unread_stmt)).scalar() or 0
            preview = None
            if last_msg:
                if last_msg.type == "text":
                    preview = last_msg.content
                elif last_msg.type == "image":
                    preview = "📷 Rasm"
                elif last_msg.type == "voice":
                    preview = "🎤 Ovozli"
                elif last_msg.type == "sticker":
                    preview = "😄 Sticker"
            chats.append({"id": chat.id, "other_user_id": other.id, "other_user_public_id": other.public_id, "other_user_nickname": other.nickname, "other_user_avatar": (other.photos or [None])[0] if other.photos else None, "is_online": other.last_seen and other.last_seen > datetime.utcnow() - __import__("datetime").timedelta(minutes=5), "last_message_preview": preview, "last_message_at": chat.last_message_at, "unread_count": unread})
        return chats

    @staticmethod
    async def get_messages(session, chat_id, user_id, before_id=None, limit=50):
        chat = await session.get(Chat, chat_id)
        if not chat or user_id not in (chat.user1_id, chat.user2_id):
            return []
        stmt = select(Message, User).join(User, User.id == Message.sender_id).where(Message.chat_id == chat_id)
        if before_id:
            stmt = stmt.where(Message.id < before_id)
        stmt = stmt.order_by(Message.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        rows = result.all()
        messages = []
        for msg, sender in rows:
            messages.append({"id": msg.id, "chat_id": chat_id, "sender_id": msg.sender_id, "sender_public_id": sender.public_id, "type": msg.type, "content": msg.content, "media_url": msg.media_url, "is_edited": msg.is_edited, "is_mine": msg.sender_id == user_id, "read_at": msg.read_at, "created_at": msg.created_at})
        await ChatService.mark_read(session, chat_id, user_id)
        return list(reversed(messages))

    @staticmethod
    async def send_message(session, chat_id, sender_id, type_, content=None, media_url=None, reply_to_id=None):
        chat = await session.get(Chat, chat_id)
        if not chat or sender_id not in (chat.user1_id, chat.user2_id):
            raise ValueError("Access denied")
        msg = Message(chat_id=chat_id, sender_id=sender_id, type=type_, content=content, media_url=media_url, reply_to_id=reply_to_id)
        session.add(msg)
        chat.last_message_at = datetime.utcnow()
        await session.commit()
        await session.refresh(msg)
        recipient_id = chat.user2_id if sender_id == chat.user1_id else chat.user1_id
        payload = {"type": "message", "data": {"id": msg.id, "chat_id": chat_id, "sender_id": sender_id, "type": type_, "content": content, "media_url": media_url, "created_at": msg.created_at.isoformat()}}
        await redis_client.publish(f"user:{recipient_id}", json.dumps(payload, default=str))
        return msg

    @staticmethod
    async def mark_read(session, chat_id, user_id):
        await session.execute(update(Message).where(and_(Message.chat_id == chat_id, Message.sender_id != user_id, Message.read_at.is_(None))).values(read_at=datetime.utcnow()))
        await session.commit()
