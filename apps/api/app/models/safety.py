"""Safety, verification, events"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.db.base import Base


class PhotoVerification(Base):
    __tablename__ = "photo_verifications"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    selfie_url = Column(Text, nullable=False)
    reference_photo_id = Column(BigInteger, nullable=False)
    status = Column(String(16), default="pending")
    confidence = Column(Float, default=0.0)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class TwoFactorAuth(Base):
    __tablename__ = "two_factor_auth"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    enabled = Column(Boolean, default=False)
    secret = Column(String(64))
    backup_codes = Column(JSON, default=list)
    last_used = Column(DateTime, nullable=True)


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False)
    relation = Column(String(32))
    created_at = Column(DateTime, default=func.now())


class SafetyReport(Base):
    __tablename__ = "safety_reports"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reporter_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reported_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(BigInteger, nullable=True)
    message_id = Column(BigInteger, nullable=True)
    reason = Column(String(64), nullable=False)
    evidence = Column(JSON, default=list)
    description = Column(Text)
    status = Column(String(16), default="pending")
    reviewed_by = Column(BigInteger, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    action_taken = Column(String(64))
    created_at = Column(DateTime, default=func.now())


class PanicEvent(Base):
    __tablename__ = "panic_events"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    contacted_id = Column(BigInteger, nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class StalkerProtection(Base):
    __tablename__ = "stalker_protection"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    block_screenshots = Column(Boolean, default=False)
    block_location = Column(Boolean, default=False)
    block_forwarded = Column(Boolean, default=False)
    mask_gps = Column(Boolean, default=False)
    fake_lat = Column(Float, nullable=True)
    fake_lon = Column(Float, nullable=True)


class DataExportRequest(Base):
    __tablename__ = "data_export_requests"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(16), default="pending")
    download_url = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    requested_at = Column(DateTime, default=func.now())


class DatePlan(Base):
    __tablename__ = "date_plans"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    match_id = Column(BigInteger, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    proposer_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(128), nullable=False)
    description = Column(Text)
    location_name = Column(String(256), nullable=False)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    planned_at = Column(DateTime, nullable=False)
    category = Column(String(32), default="general")
    cost_estimate = Column(Integer, default=0)
    status = Column(String(16), default="pending")
    created_at = Column(DateTime, default=func.now())


class DateFeedback(Base):
    __tablename__ = "date_feedback"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date_plan_id = Column(BigInteger, ForeignKey("date_plans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, default=0)
    would_meet_again = Column(Boolean, default=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
