from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from datetime import datetime
from app.services.openai_service import openai_service
from app.models.chat import Chat, ChatFolder, ChatMessage

class CRUDChat:
    @staticmethod
    def create_folder(
        db: Session,
        *,
        user_id: UUID,
        name: str,
        emoji: Optional[str] = None
    ) -> ChatFolder:
        # Получаем максимальный order_index для пользователя
        max_order = db.query(ChatFolder).filter(
            ChatFolder.user_id == user_id
        ).count()

        db_obj = ChatFolder(
            user_id=user_id,
            name=name,
            emoji=emoji,
            order_index=max_order + 1
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_chat(
        db: Session,
        *,
        user_id: UUID,
        folder_id: Optional[UUID] = None,
        title: Optional[str] = None,
        bot_style: str = "standard",
	is_memory_enabled: bool = True
    ) -> Chat:
        # Получаем следующий auto_title_number
        max_number = db.query(Chat).filter(
            Chat.user_id == user_id
        ).count()

        db_obj = Chat(
            user_id=user_id,
            folder_id=folder_id,
            title=title or f"Chat {max_number + 1}",
            auto_title_number=max_number + 1,
            bot_style=bot_style,
            is_memory_enabled=is_memory_enabled
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_chat_title_from_content(
        db: Session,
        *,
        chat_id: UUID,
        content: str
    ) -> Chat:
        """
        Обновляет название и эмодзи чата на основе содержимого сообщения
        """
        chat_obj = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat_obj:
            raise ValueError("Chat not found")

        # Генерируем название и эмодзи
        title, emoji = await openai_service.generate_chat_title(content)
        
        chat_obj.title = title
        chat_obj.emoji = emoji
        db.add(chat_obj)
        db.commit()
        db.refresh(chat_obj)
        
        return chat_obj

    @staticmethod
    def add_message(
        db: Session,
        *,
        chat_id: UUID,
        role: str,
        content: str,
        tokens_used: Optional[int] = None
    ) -> ChatMessage:
        db_obj = ChatMessage(
            chat_id=chat_id,
            role=role,
            content=content,
            tokens_used=tokens_used
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_chat(db: Session, chat_id: UUID) -> Optional[Chat]:
        return db.query(Chat).filter(Chat.id == chat_id).first()

    @staticmethod
    def get_folder(db: Session, folder_id: UUID) -> Optional[ChatFolder]:
        return db.query(ChatFolder).filter(ChatFolder.id == folder_id).first()

    @staticmethod
    def get_user_folders(
        db: Session,
        user_id: UUID
    ) -> List[ChatFolder]:
        return db.query(ChatFolder).filter(
            ChatFolder.user_id == user_id
        ).order_by(ChatFolder.order_index).all()

    @staticmethod
    def get_user_chats(
        db: Session,
        user_id: UUID,
        folder_id: Optional[UUID] = None
    ) -> List[Chat]:
        query = db.query(Chat).filter(Chat.user_id == user_id)
        if folder_id is not None:
            query = query.filter(Chat.folder_id == folder_id)
        return query.order_by(desc(Chat.created_at)).all()

    @staticmethod
    def get_chat_messages(
        db: Session,
        chat_id: UUID,
        limit: int = 50,
        before_id: Optional[UUID] = None
    ) -> List[ChatMessage]:
        query = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        )
        if before_id:
            before_message = db.query(ChatMessage).get(before_id)
            if before_message:
                query = query.filter(
                    ChatMessage.created_at < before_message.created_at
                )
        return query.order_by(desc(ChatMessage.created_at)).limit(limit).all()

    @staticmethod
    def update_chat(
        db: Session,
        *,
        db_obj: Chat,
        title: Optional[str] = None,
        folder_id: Optional[UUID] = None,
        bot_style: Optional[str] = None,
        is_memory_enabled: Optional[bool] = None
    ) -> Chat:
        if title is not None:
            db_obj.title = title
        if folder_id is not None:
            db_obj.folder_id = folder_id
        if bot_style is not None:
            db_obj.bot_style = bot_style
        if is_memory_enabled is not None:
            db_obj.is_memory_enabled = is_memory_enabled

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_folder(
        db: Session,
        *,
        db_obj: ChatFolder,
        name: Optional[str] = None,
        emoji: Optional[str] = None,
        order_index: Optional[int] = None
    ) -> ChatFolder:
        if name is not None:
            db_obj.name = name
        if emoji is not None:
            db_obj.emoji = emoji
        if order_index is not None:
            db_obj.order_index = order_index

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

chat = CRUDChat()
