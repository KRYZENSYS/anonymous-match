"""Match va Like — swipe tizimi."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Like(Base):
    """Bitta yoqtirish / super like / pass."""
    __tablename__ = "likes"
    __table_args__ = (
        Index("ix_likes_pair", "from_user_id", "to_user_id", unique=True),
        Index("ix_likes_to_user", "to_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    to_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    action: Mapped[str] = mapped_column(
        Enum("like", "pass", "superlike", name="like_action_enum"), nullable=False
    )
    is_mutual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    seen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # tomosha qildimi

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_likes")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_likes")

    def __repr__(self) -> str:
        return f"<Like from={self.from_user_id} to={self.to_user_id} action={self.action}>"


class Match(Base):
    """O'zaro like — match yuzaga keldi."""
    __tablename__ = "matches"
    __table_args__ = (
        Index("ix_matches_user1", "user1_id"),
        Index("ix_matches_user2", "user2_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Chat yaratilganmi
    chat_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("chats.id", ondelete="SET NULL"), nullable=True)

    # Kim birinchi like bosgan
    initiated_by: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_unmatched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unmatched_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Birinchi xabar yuborilganmi
    first_message_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    matched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")
    chat = relationship("Chat", foreign_keys=[chat_id])

    def get_other_user_id(self, current_user_id: int) -> int:
        return self.user2_id if current_user_id == self.user1_id else self.user1_id

    def __repr__(self) -> str:
        return f"<Match u1={self.user1_id} u2={self.user2_id}>"
