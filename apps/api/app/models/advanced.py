"""Advanced features - calls, AI, AR, photos, translation"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.db.base import Base


class Call(Base):
    __tablename__ = "calls"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    caller_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    callee_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(16), nullable=False)
    status = Column(String(16), default="ringing")
    channel_name = Column(String(128), nullable=False)
    started_at = Column(DateTime, default=func.now())
    answered_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Integer, default=0)
    cost_coins = Column(Integer, default=0)
    recording_url = Column(Text, nullable=True)


class PhotoScore(Base):
    __tablename__ = "photo_scores"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    photo_url = Column(String(512), nullable=False)
    ai_score = Column(Float, default=0.0)
    likes_received = Column(Integer, default=0)
    is_best_photo = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class CompatibilityScore(Base):
    __tablename__ = "compatibility_scores"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user1_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, default=0.0)
    interest_score = Column(Float, default=0.0)
    age_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    personality_score = Column(Float, default=0.0)
    lifestyle_score = Column(Float, default=0.0)
    details = Column(JSON, default=dict)
    calculated_at = Column(DateTime, default=func.now())


class TranslationCache(Base):
    __tablename__ = "translation_cache"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_text = Column(Text, nullable=False)
    source_lang = Column(String(8), nullable=False)
    target_lang = Column(String(8), nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)
    seen = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    matched = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class ConversationStarter(Base):
    __tablename__ = "conversation_starters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    category = Column(String(32), default="general")
    language = Column(String(8), default="uz")
    is_active = Column(Boolean, default=True)
    uses = Column(Integer, default=0)


class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sentiment = Column(String(16))
    score = Column(Float, default=0.0)
    emotions = Column(JSON, default=dict)
    is_toxic = Column(Boolean, default=False)
    toxicity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())


class ChatInsight(Base):
    __tablename__ = "chat_insights"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    user1_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_messages = Column(Integer, default=0)
    response_time_avg = Column(Float, default=0.0)
    sentiment_avg = Column(Float, default=0.0)
    conversation_streak = Column(Integer, default=0)
    last_message_at = Column(DateTime, nullable=True)
    compatibility_pct = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ReferralProgram(Base):
    __tablename__ = "referral_programs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    referrer_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    referee_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(32), nullable=False)
    status = Column(String(16), default="pending")
    referrer_reward = Column(Integer, default=0)
    referee_reward = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class ChatTranslation(Base):
    __tablename__ = "chat_translations"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    target_lang = Column(String(8), nullable=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
