"""Database — async SQLAlchemy 2.0 + Alembic."""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


engine = create_async_engine(
    settings.db_url,
    echo=settings.APP_DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db():
    """DB ishga tushganda — jadvallar yaratish (test uchun)."""
    # Production'da Alembic ishlatamiz, lekin birinchi marta avtomatik yaratish ham qulay
    async with engine.begin() as conn:
        # Import all models
        from app.models import (  # noqa
            User, Profile, Match, Like, Chat, Message, Media,
            Report, Block, Notification, Premium, Subscription, Log,
        )
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
