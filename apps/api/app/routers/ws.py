"""WebSocket router — real-time chat va notification."""
from __future__ import annotations

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.deps import get_current_user
from app.core.redis_client import get_redis
from app.core.security import decode_token
from app.models import User, Chat, Message, Notification
from app.services.chat_service import ChatService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    """WebSocket connectionlarni boshqarish."""

    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = {}
        self.chat_subscribers: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active_connections.setdefault(user_id, set()).add(ws)
        # Online
        redis = get_redis()
        await redis.sadd("online_users", str(user_id))

    async def disconnect(self, user_id: int, ws: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(ws)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Offline
                redis = get_redis()
                await redis.srem("online_users", str(user_id))

    async def send_personal(self, user_id: int, data: dict):
        if user_id in self.active_connections:
            for ws in list(self.active_connections[user_id]):
                try:
                    await ws.send_json(data)
                except Exception:
                    pass

    async def broadcast(self, data: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_personal(user_id, data)


manager = ConnectionManager()


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    Asosiy WebSocket ulanish.
    Frontend: ws://host/ws/connect?token=JWT_TOKEN
    """
    # Auth
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # DB dan user olish
    async with async_session_maker() as db:
        res = await db.execute(select(User).where(User.id == user_id))
        user = res.scalar_one_or_none()
        if not user or user.is_banned:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Connect
        await manager.connect(user_id, websocket)
        await UserService.set_online(db, user, True)

        # Redis subscribe
        redis = get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"notify:{user_id}")

        try:
            await websocket.send_json({
                "type": "connected",
                "data": {"user_id": user_id, "public_id": user.public_id},
            })

            async def listen_redis():
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            await websocket.send_json(data)
                        except Exception:
                            pass

            import asyncio
            listen_task = asyncio.create_task(listen_redis())

            # Clientdan xabarlarni qabul qilish
            while True:
                raw = await websocket.receive_text()
                try:
                    msg = json.loads(raw)
                    msg_type = msg.get("type")
                    if msg_type == "ping":
                        await websocket.send_json({"type": "pong", "ts": datetime.utcnow().isoformat()})
                    elif msg_type == "typing":
                        # Typing indicator
                        chat_id = msg.get("chat_id")
                        is_typing = msg.get("is_typing", False)
                        if chat_id:
                            await ChatService.set_typing(db, user, chat_id, is_typing)
                    elif msg_type == "read":
                        chat_id = msg.get("chat_id")
                        message_ids = msg.get("message_ids", [])
                        if chat_id:
                            await ChatService.mark_as_read(db, user, chat_id, message_ids)
                    elif msg_type == "heartbeat":
                        user.last_active_at = datetime.utcnow()
                except json.JSONDecodeError:
                    pass

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WS error: {e}")
        finally:
            listen_task.cancel()
            await pubsub.unsubscribe(f"notify:{user_id}")
            await pubsub.close()
            await manager.disconnect(user_id, websocket)
            await UserService.set_online(db, user, False)


@router.websocket("/chat/{chat_id}")
async def chat_websocket(
    websocket: WebSocket,
    chat_id: int,
    token: str = Query(...),
):
    """
    Chat xonasi uchun WebSocket.
    Faqat shu chat'dagi xabarlarni qabul qiladi.
    """
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with async_session_maker() as db:
        res = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = res.scalar_one_or_none()
        if not chat or user_id not in (chat.user1_id, chat.user2_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()
        manager.chat_subscribers.setdefault(chat_id, set()).add(websocket)

        redis = get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"chat:{chat_id}")

        try:
            await websocket.send_json({"type": "connected", "data": {"chat_id": chat_id}})

            import asyncio
            async def listen():
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            await websocket.send_json(data)
                        except Exception:
                            pass

            listen_task = asyncio.create_task(listen())

            while True:
                raw = await websocket.receive_text()
                try:
                    msg = json.loads(raw)
                    if msg.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except json.JSONDecodeError:
                    pass

        except WebSocketDisconnect:
            pass
        finally:
            listen_task.cancel()
            await pubsub.unsubscribe(f"chat:{chat_id}")
            await pubsub.close()
            if chat_id in manager.chat_subscribers:
                manager.chat_subscribers[chat_id].discard(websocket)
                if not manager.chat_subscribers[chat_id]:
                    del manager.chat_subscribers[chat_id]
