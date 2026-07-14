"""Report va Block — xavfsizlik."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Report(Base):
    """Foydalanuvchini report qilish."""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reported_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Sabab
    reason: Mapped[str] = mapped_column(
        Enum(
            "spam", "fake_profile", "inappropriate", "harassment", "scam",
            "underage", "hate_speech", "doxing", "other",
            name="report_reason_enum"
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Dalil
    evidence_chat_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_media_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Moderatsiya
    status: Mapped[str] = mapped_column(
        Enum("pending", "reviewing", "resolved", "dismissed", name="report_status_enum"),
        default="pending", nullable=False
    )
    moderator_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    moderator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(String(64), nullable=True)  # banned | warned | suspended | no_action

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="sent_reports")
    reported = relationship("User", foreign_keys=[reported_id], back_populates="received_reports")

    def __repr__(self) -> str:
        return f"<Report {self.reporter_id} -> {self.reported_id} reason={self.reason}>"


class Block(Base):
    """Foydalanuvchini bloklash."""
    __tablename__ = "blocks"
    __table_args__ = (
        # Block pair unique
        {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blocker_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    blocked_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocked_users")

    def __repr__(self) -> str:
        return f"<Block {self.blocker_id} blocked {self.blocked_id}>"
