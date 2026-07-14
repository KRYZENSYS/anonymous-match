"""Community models - groups, events, forums, live streams, NFT, AR"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.db.base import Base


class Group(Base):
    __tablename__ = "groups"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    cover_url = Column(Text)
    icon = Column(String(16))
    category = Column(String(32), default="general")  # city, hobby, age, religion, lgbt
    type = Column(String(16), default="public")  # public, private, invite
    rules = Column(Text)
    member_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=func.now())


class GroupMember(Base):
    __tablename__ = "group_members"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(16), default="member")  # member, moderator, admin
    joined_at = Column(DateTime, default=func.now())


class GroupPost(Base):
    __tablename__ = "group_posts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=list)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class Event(Base):
    __tablename__ = "events"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    cover_url = Column(Text)
    category = Column(String(32), default="meetup")  # meetup, speed_dating, party, workshop
    location_name = Column(String(256))
    location_lat = Column(Float)
    location_lon = Column(Float)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    capacity = Column(Integer, default=0)
    attendees_count = Column(Integer, default=0)
    ticket_price = Column(Integer, default=0)  # coins
    is_online = Column(Boolean, default=False)
    meeting_url = Column(String(512), nullable=True)
    status = Column(String(16), default="upcoming")
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=func.now())


class EventAttendee(Base):
    __tablename__ = "event_attendees"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(BigInteger, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(16), default="going")  # going, maybe, declined
    ticket_paid = Column(Integer, default=0)
    joined_at = Column(DateTime, default=func.now())


class ForumThread(Base):
    __tablename__ = "forum_threads"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category = Column(String(64), nullable=False)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    views = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class ForumReply(Base):
    __tablename__ = "forum_replies"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(BigInteger, ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class LiveStream(Base):
    __tablename__ = "live_streams"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    host_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(256))
    description = Column(Text)
    stream_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text)
    visibility = Column(String(16), default="public")  # public, matches, premium
    viewers_count = Column(Integer, default=0)
    is_live = Column(Boolean, default=False)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    gifts_received = Column(Integer, default=0)


class NFTAvatar(Base):
    __tablename__ = "nft_avatars"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    image_url = Column(Text, nullable=False)
    style = Column(String(32), default="anime")  # anime, cartoon, realistic, cyberpunk
    prompt = Column(Text, nullable=True)
    ton_wallet = Column(String(128), nullable=True)
    transaction_hash = Column(String(128), nullable=True)
    is_listed = Column(Boolean, default=False)
    price = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class CoinPackage(Base):
    __tablename__ = "coin_packages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    coins = Column(Integer, nullable=False)
    bonus_coins = Column(Integer, default=0)
    price_stars = Column(Integer, nullable=False)
    price_usd = Column(Float, nullable=False)
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
