"""Seasonal, travel, charity, modes"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.db.base import Base


class SeasonalEvent(Base):
    __tablename__ = "seasonal_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    code = Column(String(32), unique=True, nullable=False)
    description = Column(Text)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    theme_color = Column(String(16), default="#f43f5e")
    icon = Column(String(8))
    bonus_multiplier = Column(Float, default=1.0)
    special_features = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)


class TravelMode(Base):
    __tablename__ = "travel_modes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_city = Column(String(64), nullable=True)
    current_country = Column(String(64), nullable=True)
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    started_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class CharityDonation(Base):
    __tablename__ = "charity_donations"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_id = Column(BigInteger, nullable=True)
    amount_usd = Column(Float, nullable=False)
    charity = Column(String(128), nullable=False)
    transaction_hash = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=func.now())


class AnonymousProfile(Base):
    __tablename__ = "anonymous_profiles"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    anonymous_avatar = Column(String(512), nullable=True)
    incognito_mode = Column(Boolean, default=False)
    hide_from_feed = Column(Boolean, default=False)
    hide_distance = Column(Boolean, default=False)
    hide_age = Column(Boolean, default=False)
    hide_last_seen = Column(Boolean, default=False)


class ABTest(Base):
    __tablename__ = "ab_tests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    variants = Column(JSON, nullable=False)
    metrics = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, default=func.now())
    ends_at = Column(DateTime, nullable=True)


class ABTestAssignment(Base):
    __tablename__ = "ab_test_assignments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("ab_tests.id", ondelete="CASCADE"), nullable=False)
    variant = Column(String(64), nullable=False)
    assigned_at = Column(DateTime, default=func.now())


class ABTestEvent(Base):
    __tablename__ = "ab_test_events"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assignment_id = Column(BigInteger, ForeignKey("ab_test_assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    event_name = Column(String(64), nullable=False)
    value = Column(Float, default=0.0)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    tier = Column(Integer, default=1)
    price_stars = Column(Integer, nullable=False)
    price_usd = Column(Float, nullable=False)
    duration_days = Column(Integer, default=30)
    features = Column(JSON, default=list)
    boost_count = Column(Integer, default=0)
    superlikes_per_day = Column(Integer, default=0)
    is_vip = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    advertiser = Column(String(128))
    type = Column(String(32), default="banner")
    image_url = Column(Text, nullable=True)
    target_url = Column(Text, nullable=True)
    target_regions = Column(JSON, default=list)
    target_age_min = Column(Integer, default=18)
    target_age_max = Column(Integer, default=99)
    target_genders = Column(JSON, default=list)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, default=func.now())
    ends_at = Column(DateTime, nullable=True)


class SponsoredProfile(Base):
    __tablename__ = "sponsored_profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    budget_stars = Column(Integer, nullable=False)
    spent_stars = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    starts_at = Column(DateTime, default=func.now())
    ends_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
