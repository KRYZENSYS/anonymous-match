"""Bot middlewares: auth, throttle, admin"""
import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from app.core.redis import redis_client
from app.services.user import UserService
from app.db.session import async_session_maker


class AuthMiddleware(BaseMiddleware):
    """Inject user record into handler data"""

    async def __call__(self, handler: Callable, event: TelegramObject, data: Dict[str, Any]) -> Any:
        tg_user: TgUser = data.get("event_from_user")
        if not tg_user:
            return await handler(event, data)

        async with async_session_maker() as session:
            user, is_new = await UserService.get_or_create(
                session,
                telegram_id=tg_user.id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username,
                language_code=tg_user.language_code,
                is_premium=tg_user.is_premium or False,
            )
            data["user"] = user
            data["is_new"] = is_new
        return await handler(event, data)


class ThrottleMiddleware(BaseMiddleware):
    """Simple rate limit per user"""

    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit

    async def __call__(self, handler, event, data):
        tg_user = data.get("event_from_user")
        if not tg_user:
            return await handler(event, data)
        key = f"throttle:{tg_user.id}"
        last = await redis_client.get(key)
        now = time.time()
        if last and now - float(last) < self.rate_limit:
            return  # Silent drop
        await redis_client.setex(key, 2, str(now))
        return await handler(event, data)


class AdminMiddleware(BaseMiddleware):
    """Restrict handlers to admin users"""

    async def __call__(self, handler, event, data):
        if data.get("command") and data["command"].command in ("admin", "stats", "broadcast", "ban"):
            tg_user = data.get("event_from_user")
            if tg_user and tg_user.id not in settings.ADMIN_TELEGRAM_IDS:
                return  # Block
        return await handler(event, data)


from app.core.config import settings
