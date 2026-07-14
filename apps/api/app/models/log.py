"""Log modeli — audit, admin actions, system events."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Log(Base):
    """Tizim loglari va admin audit."""
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Log turi
    level: Mapped[str] = mapped_column(
        Enum("debug", "info", "warning", "error", "critical", "audit", name="log_level_enum"),
        default="info", nullable=False
    )
    category: Mapped[str] = mapped_column(
        Enum(
            "auth", "profile", "match", "chat", "payment", "admin",
            "security", "system", "bot", "api", "websocket",
            name="log_category_enum"
        ),
        nullable=False
    )

    # Action
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Qo'shimcha
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Texnik
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 support
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="logs")

    def __repr__(self) -> str:
        return f"<Log [{self.level}] {self.action}: {self.message[:50]}>"
