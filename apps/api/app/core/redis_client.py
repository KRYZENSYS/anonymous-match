"""Redis — async client + pubsub helpers."""
import redis.asyncio as redis

from app.core.config import settings

_redis: redis.Redis | None = None


async def init_redis():
    global _redis
    _redis = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50,
    )
    await _redis.ping()


async def close_redis():
    if _redis:
        await _redis.close()


def get_redis() -> redis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis


# ===== WebSocket pubsub channels =====
def chat_channel(chat_id: int) -> str:
    return f"chat:{chat_id}"


def notify_channel(user_id: int) -> str:
    return f"notify:{user_id}"


def online_channel() -> str:
    return "online_users"
