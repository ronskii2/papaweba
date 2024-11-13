from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, String, Integer, ForeignKey, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from sqlalchemy import DateTime

class ChatFolder(Base):
    __tablename__ = 'chat_folders'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emoji: Mapped[Optional[str]] = mapped_column(String(10))
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="chat_folders")
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="folder", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = 'chats'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    folder_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('chat_folders.id', ondelete='SET NULL'))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    emoji: Mapped[Optional[str]] = mapped_column(String(10))
    auto_title_number: Mapped[Optional[int]] = mapped_column(Integer)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    bot_style: Mapped[Optional[str]] = mapped_column(String(50))
    is_memory_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="chats")
    folder: Mapped[Optional["ChatFolder"]] = relationship("ChatFolder", back_populates="chats")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    chat_id: Mapped[UUID] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)

    # Отношения
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
