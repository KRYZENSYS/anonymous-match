"""Chat enhancement models - voice/video messages, stickers, polls, scheduled"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class StickerPack(Base):
    __tablename__ = "sticker_packs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    cover_url = Column(Text)
    category = Column(String(32), default="general")
    price_coins = Column(Integer, default=0)
    is_free = Column(Boolean, default=True)
    is_animated = Column(Boolean, default=False)
    sticker_count = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class Sticker(Base):
    __tablename__ = "stickers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pack_id = Column(Integer, ForeignKey("sticker_packs.id", ondelete="CASCADE"), nullable=False, index=True)
    emoji = Column(String(8))
    image_url = Column(Text, nullable=False)
    order = Column(Integer, default=0)


class UserStickerPack(Base):
    __tablename__ = "user_sticker_packs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pack_id = Column(Integer, ForeignKey("sticker_packs.id", ondelete="CASCADE"), nullable=False)


class MessageReaction(Base):
    __tablename__ = "message_reactions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    emoji = Column(String(8), nullable=False)
    created_at = Column(DateTime, default=func.now())


class ChatTheme(Base):
    __tablename__ = "chat_themes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    code = Column(String(32), unique=True, nullable=False)
    background_url = Column(Text, nullable=True)
    bubble_color_user = Column(String(16))
    bubble_color_other = Column(String(16))
    text_color = Column(String(16))
    preview_url = Column(Text, nullable=True)
    price_coins = Column(Integer, default=0)
    is_free = Column(Boolean, default=True)
    is_seasonal = Column(Boolean, default=False)


class UserChatTheme(Base):
    __tablename__ = "user_chat_themes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=True)  # null = default for all
    theme_id = Column(Integer, ForeignKey("chat_themes.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)


class ScheduledMessage(Base):
    __tablename__ = "scheduled_messages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(16), default="text")
    content = Column(Text)
    media_url = Column(Text, nullable=True)
    send_at = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Poll(Base):
    __tablename__ = "polls"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question = Column(String(256), nullable=False)
    options = Column(JSON, nullable=False)  # ["Kino", "Serial", "Konsert"]
    is_multi = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class PollVote(Base):
    __tablename__ = "poll_votes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    poll_id = Column(BigInteger, ForeignKey("polls.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    option_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())


class PinnedMessage(Base):
    __tablename__ = "pinned_messages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    pinned_by = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pinned_at = Column(DateTime, default=func.now())


class SavedMessage(Base):
    __tablename__ = "saved_messages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, default=func.now())


class ForwardedMessage(Base):
    __tablename__ = "forwarded_messages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    from_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    from_chat_id = Column(BigInteger, nullable=True)
