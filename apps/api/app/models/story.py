"""Story model - 24-hour ephemeral content"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class Story(Base):
    __tablename__ = "stories"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(String(16), nullable=False)  # image, video
    media_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    text_overlay = Column(Text, nullable=True)
    background_color = Column(String(16), default="#000000")
    duration = Column(Integer, default=5)
    views_count = Column(Integer, default=0)
    is_highlight = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class StoryView(Base):
    __tablename__ = "story_views"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    story_id = Column(BigInteger, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    viewer_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())


class StoryReaction(Base):
    __tablename__ = "story_reactions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    story_id = Column(BigInteger, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reaction = Column(String(16), nullable=False)
    created_at = Column(DateTime, default=func.now())


class StoryReply(Base):
    __tablename__ = "story_replies"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    story_id = Column(BigInteger, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
