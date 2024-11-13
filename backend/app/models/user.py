from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    about_me: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    reset_password_token: Mapped[Optional[str]] = mapped_column(String(255))
    reset_password_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    ai_model: Mapped[str] = mapped_column(
        String(50), 
        default="claude-3-5-sonnet-20241022",
        nullable=False
    )
    default_bot_style: Mapped[str] = mapped_column(
        String(50), 
        default="standard",
        nullable=False
    )
    # Отношения
    chat_folders: Mapped[List["ChatFolder"]] = relationship("ChatFolder", back_populates="user", cascade="all, delete-orphan")
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[List["UserSubscription"]] = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    tool_usages: Mapped[List["ToolUsage"]] = relationship("ToolUsage", back_populates="user", cascade="all, delete-orphan")
    images: Mapped[List["UserImage"]] = relationship("UserImage", back_populates="user", cascade="all, delete-orphan")
