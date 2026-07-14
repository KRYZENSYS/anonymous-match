"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-07-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("telegram_id", sa.BigInteger, unique=True, nullable=False, index=True),
        sa.Column("telegram_username", sa.String(64), nullable=True),
        sa.Column("telegram_first_name", sa.String(128), nullable=True),
        sa.Column("telegram_photo_url", sa.String(512), nullable=True),
        sa.Column("telegram_language_code", sa.String(8), nullable=True),
        sa.Column("is_telegram_premium", sa.Boolean, default=False),
        sa.Column("public_id", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("role", sa.String(16), default="user", nullable=False),
        sa.Column("is_admin", sa.Boolean, default=False, nullable=False),
        sa.Column("is_banned", sa.Boolean, default=False, nullable=False),
        sa.Column("is_suspended", sa.Boolean, default=False, nullable=False),
        sa.Column("suspended_until", sa.DateTime, nullable=True),
        sa.Column("ban_reason", sa.String(512), nullable=True),
        sa.Column("is_online", sa.Boolean, default=False, nullable=False),
        sa.Column("last_seen", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_active_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("device_id", sa.String(64), nullable=True),
        sa.Column("push_token", sa.String(256), nullable=True),
        sa.Column("webapp_version", sa.String(16), nullable=True),
        sa.Column("preferred_language", sa.String(8), default="uz"),
        sa.Column("theme", sa.String(8), default="dark"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)
    op.create_index("ix_users_public_id", "users", ["public_id"], unique=True)

    # Profiles
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("nickname", sa.String(32), nullable=False),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("birth_date", sa.Date, nullable=False),
        sa.Column("gender", sa.Enum("male", "female", "other", name="gender_enum"), nullable=False),
        sa.Column("looking_for", sa.Enum("male", "female", "everyone", name="looking_for_enum"), default="everyone"),
        sa.Column("region", sa.String(64), nullable=True),
        sa.Column("city", sa.String(64), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("interests", postgresql.ARRAY(sa.String(32)), default=list),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("photos", postgresql.ARRAY(sa.String(512)), default=list),
        sa.Column("height_cm", sa.Integer, nullable=True),
        sa.Column("occupation", sa.String(64), nullable=True),
        sa.Column("education", sa.String(64), nullable=True),
        sa.Column("languages", postgresql.ARRAY(sa.String(8)), default=list),
        sa.Column("min_age_preference", sa.Integer, default=18),
        sa.Column("max_age_preference", sa.Integer, default=99),
        sa.Column("max_distance_km", sa.Integer, default=100),
        sa.Column("show_only_online", sa.Boolean, default=False),
        sa.Column("show_only_in_region", sa.Boolean, default=False),
        sa.Column("boost_expires_at", sa.Date, nullable=True),
        sa.Column("is_boosted", sa.Boolean, default=False),
        sa.Column("is_complete", sa.Boolean, default=False),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("profile_views", sa.Integer, default=0),
        sa.Column("likes_received", sa.Integer, default=0),
        sa.Column("likes_sent", sa.Integer, default=0),
        sa.Column("match_count", sa.Integer, default=0),
        sa.Column("created_at", sa.Date, server_default=sa.func.current_date()),
        sa.Column("updated_at", sa.Date, server_default=sa.func.current_date()),
    )

    # Likes
    op.create_table(
        "likes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("from_user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.Enum("like", "pass", "superlike", name="like_action_enum"), nullable=False),
        sa.Column("is_mutual", sa.Boolean, default=False),
        sa.Column("seen", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_likes_pair", "likes", ["from_user_id", "to_user_id"], unique=True)
    op.create_index("ix_likes_to_user", "likes", ["to_user_id"])

    # Matches
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user1_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user2_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chat_id", sa.Integer, nullable=True),
        sa.Column("initiated_by", sa.Integer, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_unmatched", sa.Boolean, default=False),
        sa.Column("unmatched_by", sa.Integer, nullable=True),
        sa.Column("first_message_sent", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("matched_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Chats
    op.create_table(
        "chats",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user1_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user2_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("direct", "match", name="chat_type_enum"), default="direct"),
        sa.Column("match_id", sa.Integer, sa.ForeignKey("matches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("last_message_at", sa.DateTime, nullable=True),
        sa.Column("last_message_preview", sa.String(255), nullable=True),
        sa.Column("user1_unread", sa.Integer, default=0),
        sa.Column("user2_unread", sa.Integer, default=0),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_archived_u1", sa.Boolean, default=False),
        sa.Column("is_archived_u2", sa.Boolean, default=False),
        sa.Column("is_blocked", sa.Boolean, default=False),
        sa.Column("blocked_by", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Media
    op.create_table(
        "media",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("avatar", "photo", "video", "voice", "sticker", "gif", "file", name="media_type_enum"), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("thumbnail_url", sa.String(1024), nullable=True),
        sa.Column("public_id", sa.String(128), nullable=True),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(64), nullable=True),
        sa.Column("size_bytes", sa.BigInteger, nullable=True),
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("duration_sec", sa.Integer, nullable=True),
        sa.Column("is_moderated", sa.Boolean, default=False),
        sa.Column("is_safe", sa.Boolean, default=True),
        sa.Column("moderation_score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Messages
    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.Integer, sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("text", "image", "video", "voice", "sticker", "gif", "file", "system", name="message_type_enum"), default="text"),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("media_id", sa.Integer, sa.ForeignKey("media.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reply_to_id", sa.BigInteger, sa.ForeignKey("messages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("extra", postgresql.JSONB, nullable=True),
        sa.Column("is_edited", sa.Boolean, default=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("deleted_for_everyone", sa.Boolean, default=False),
        sa.Column("deleted_by", sa.Integer, nullable=True),
        sa.Column("read_at", sa.DateTime, nullable=True),
        sa.Column("delivered_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_messages_chat_id", "messages", ["chat_id"])
    op.create_index("ix_messages_sender_id", "messages", ["sender_id"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])

    # Reports
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("reporter_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reported_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.Enum("spam", "fake_profile", "inappropriate", "harassment", "scam", "underage", "hate_speech", "doxing", "other", name="report_reason_enum"), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("evidence_chat_id", sa.Integer, nullable=True),
        sa.Column("evidence_message_id", sa.Integer, nullable=True),
        sa.Column("evidence_media_id", sa.Integer, nullable=True),
        sa.Column("status", sa.Enum("pending", "reviewing", "resolved", "dismissed", name="report_status_enum"), default="pending"),
        sa.Column("moderator_id", sa.Integer, nullable=True),
        sa.Column("moderator_note", sa.Text, nullable=True),
        sa.Column("action_taken", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
    )

    # Blocks
    op.create_table(
        "blocks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("blocker_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("blocked_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Notifications
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("new_match", "new_message", "new_like", "super_like", "profile_view", "chat_request", "boost_active", "premium_expiring", "system", "announcement", "report_resolved", name="notification_type_enum"), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("body", sa.String(512), nullable=False),
        sa.Column("icon", sa.String(8), nullable=True),
        sa.Column("data", sa.JSON, nullable=True),
        sa.Column("related_user_id", sa.Integer, nullable=True),
        sa.Column("related_chat_id", sa.Integer, nullable=True),
        sa.Column("related_match_id", sa.Integer, nullable=True),
        sa.Column("is_read", sa.Boolean, default=False),
        sa.Column("read_at", sa.DateTime, nullable=True),
        sa.Column("sent_push", sa.Boolean, default=False),
        sa.Column("sent_telegram", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Premium
    op.create_table(
        "premium",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("is_premium", sa.Boolean, default=False),
        sa.Column("tier", sa.Enum("none", "plus", "gold", "platinum", name="premium_tier_enum"), default="none"),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("is_active", sa.Boolean, default=False),
        sa.Column("boost_count", sa.Integer, default=0),
        sa.Column("last_boost_at", sa.DateTime, nullable=True),
        sa.Column("super_likes_used", sa.Integer, default=0),
        sa.Column("super_likes_limit", sa.Integer, default=1),
        sa.Column("likes_used_today", sa.Integer, default=0),
        sa.Column("likes_limit", sa.Integer, default=50),
        sa.Column("likes_reset_at", sa.DateTime, nullable=True),
        sa.Column("profile_views_seen", sa.Integer, default=0),
        sa.Column("auto_renew", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tier", sa.String(16), nullable=False),
        sa.Column("duration_days", sa.Integer, nullable=False),
        sa.Column("price_stars", sa.Integer, nullable=False),
        sa.Column("price_usd", sa.Float, default=0.0),
        sa.Column("payment_method", sa.Enum("telegram_stars", "card", "crypto", "admin_grant", name="payment_method_enum"), default="telegram_stars"),
        sa.Column("payment_id", sa.String(128), nullable=True),
        sa.Column("payment_charge_id", sa.String(128), nullable=True),
        sa.Column("status", sa.Enum("pending", "paid", "active", "expired", "cancelled", "refunded", name="subscription_status_enum"), default="pending"),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("cancelled_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Logs
    op.create_table(
        "logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("level", sa.Enum("debug", "info", "warning", "error", "critical", "audit", name="log_level_enum"), default="info"),
        sa.Column("category", sa.Enum("auth", "profile", "match", "chat", "payment", "admin", "security", "system", "bot", "api", "websocket", name="log_category_enum"), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("logs")
    op.drop_table("subscriptions")
    op.drop_table("premium")
    op.drop_table("notifications")
    op.drop_table("blocks")
    op.drop_table("reports")
    op.drop_table("messages")
    op.drop_table("media")
    op.drop_table("chats")
    op.drop_table("matches")
    op.drop_table("likes")
    op.drop_table("profiles")
    op.drop_table("users")
