"""Gamification models - coins, achievements, streaks, missions, gifts"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.sql import func
from app.db.base import Base


class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # positive or negative
    type = Column(String(32), nullable=False)  # earned, spent, gift, bonus, purchase
    reason = Column(String(128), nullable=True)
    ref_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    icon = Column(String(16))
    reward_coins = Column(Integer, default=0)
    condition_type = Column(String(32))  # matches, messages, days, profile
    condition_value = Column(Integer, default=1)
    tier = Column(String(16), default="bronze")  # bronze, silver, gold, platinum, diamond


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Integer, default=0)
    unlocked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Streak(Base):
    __tablename__ = "streaks"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_login = Column(Date, nullable=True)
    total_logins = Column(Integer, default=0)


class Mission(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    type = Column(String(32))  # daily, weekly, monthly
    target = Column(Integer, default=1)
    reward_coins = Column(Integer, default=0)
    reward_superlikes = Column(Integer, default=0)
    reward_boost = Column(Integer, default=0)


class UserMission(Base):
    __tablename__ = "user_missions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Integer, default=0)
    target = Column(Integer, default=1)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())


class Gift(Base):
    __tablename__ = "gifts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    icon = Column(String(16), default="🎁")
    image_url = Column(Text, nullable=True)
    price_coins = Column(Integer, nullable=False)
    animation_url = Column(Text, nullable=True)
    category = Column(String(32), default="general")  # romantic, fun, premium, seasonal


class GiftTransaction(Base):
    __tablename__ = "gift_transactions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    gift_id = Column(Integer, ForeignKey("gifts.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="SET NULL"), nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())


class SpinReward(Base):
    __tablename__ = "spin_rewards"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reward_type = Column(String(32))  # coins, superlike, boost, premium
    reward_value = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class Leaderboard(Base):
    __tablename__ = "leaderboard"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_score = Column(Integer, default=0)
    matches = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    photos_uploaded = Column(Integer, default=0)
    days_active = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
