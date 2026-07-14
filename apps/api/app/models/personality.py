"""Personality test, prompts, voice intro"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class PersonalityTest(Base):
    __tablename__ = "personality_tests"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mbti_type = Column(String(8), nullable=True)
    big_five = Column(JSON, default=dict)
    love_language = Column(String(32))
    answers = Column(JSON, default=dict)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    category = Column(String(32), default="general")
    placeholder = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)


class UserPrompt(Base):
    __tablename__ = "user_prompts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    answer = Column(Text, nullable=False)
    order = Column(Integer, default=0)


class TopFive(Base):
    __tablename__ = "top_fives"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    movies = Column(JSON, default=list)
    songs = Column(JSON, default=list)
    books = Column(JSON, default=list)
    foods = Column(JSON, default=list)
    travel = Column(JSON, default=list)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class VoiceIntro(Base):
    __tablename__ = "voice_intros"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    audio_url = Column(Text, nullable=False)
    duration = Column(Integer, default=0)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())


class VideoIntro(Base):
    __tablename__ = "video_intros"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    video_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text)
    duration = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class SocialLink(Base):
    __tablename__ = "social_links"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    instagram = Column(String(64))
    tiktok = Column(String(64))
    spotify = Column(String(128))
    telegram = Column(String(64))
    twitter = Column(String(64))
    youtube = Column(String(128))
    linkedin = Column(String(128))
    website = Column(String(256))


class LifestyleTag(Base):
    __tablename__ = "lifestyle_tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    icon = Column(String(8))
    category = Column(String(32), default="lifestyle")


class UserLifestyleTag(Base):
    __tablename__ = "user_lifestyle_tags"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("lifestyle_tags.id", ondelete="CASCADE"), nullable=False)
