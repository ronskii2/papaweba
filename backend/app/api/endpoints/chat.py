from app.models.chat import Chat, ChatFolder, ChatMessage
from app.services.limits import limits_service
from app.services.anthropic import anthropic_service
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.crud.chats import chat
from app.schemas.chat import (
    ChatFolderCreate,
    ChatFolderUpdate,
    ChatFolderInDB,
    ChatCreate,
    ChatUpdate,
    ChatInDB,
    ChatMessageCreate,
    ChatMessageInDB
)
from app.models.user import User

router = APIRouter()

# Папки чатов
@router.post("/folders/", response_model=ChatFolderInDB)
async def create_chat_folder(
    *,
    db: Session = Depends(get_db),
    folder_in: ChatFolderCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Создать новую папку для чатов.
    """
    return chat.create_folder(db=db, user_id=current_user.id, **folder_in.dict())

@router.get("/folders/", response_model=List[ChatFolderInDB])
async def get_chat_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить все папки чатов текущего пользователя.
    """
    return chat.get_user_folders(db=db, user_id=current_user.id)

@router.put("/folders/{folder_id}", response_model=ChatFolderInDB)
async def update_chat_folder(
    *,
    db: Session = Depends(get_db),
    folder_id: UUID,
    folder_in: ChatFolderUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Обновить папку чатов.
    """
    folder = chat.get_folder(db=db, folder_id=folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Chat folder not found")
    if folder.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return chat.update_folder(db=db, db_obj=folder, **folder_in.dict(exclude_unset=True))

# Чаты
@router.post("/", response_model=ChatInDB)
async def create_chat(
    *,
    db: Session = Depends(get_db),
    chat_in: ChatCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый чат.
    """
    if chat_in.folder_id:
        folder = chat.get_folder(db=db, folder_id=chat_in.folder_id)
        if not folder or folder.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Chat folder not found")
    
    # Используем стиль бота по умолчанию, если не указан другой
    bot_style = chat_in.bot_style or current_user.default_bot_style
    
    return chat.create_chat(
        db=db, 
        user_id=current_user.id, 
        bot_style=bot_style,
        **chat_in.dict(exclude={'bot_style'})
    )

@router.get("/", response_model=List[ChatInDB])
async def get_chats(
    db: Session = Depends(get_db),
    folder_id: UUID = None,
    current_user: User = Depends(get_current_user)
):
    """
    Получить все чаты пользователя, опционально фильтруя по папке.
    """
    return chat.get_user_chats(db=db, user_id=current_user.id, folder_id=folder_id)

@router.get("/{chat_id}", response_model=ChatInDB)
async def get_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Получить конкретный чат по ID.
    """
    chat_obj = chat.get_chat(db=db, chat_id=chat_id)
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return chat_obj

@router.put("/{chat_id}", response_model=ChatInDB)
async def update_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: UUID,
    chat_in: ChatUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Обновить чат.
    """
    chat_obj = chat.get_chat(db=db, chat_id=chat_id)
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return chat.update_chat(db=db, db_obj=chat_obj, **chat_in.dict(exclude_unset=True))


@router.get("/limits/", response_model=Dict[str, Any])
async def get_chat_limits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о лимитах чата.
    """
    return await limits_service.check_chat_limits(
        db, 
        str(current_user.id), 
        throw_exception=False
    )


# Сообщения
@router.post("/{chat_id}/messages/", response_model=ChatMessageInDB)
async def create_message(
    *,
    db: Session = Depends(get_db),
    chat_id: UUID,
    message_in: ChatMessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Добавить сообщение в чат и получить ответ от Claude.
    """
    # Проверяем лимиты перед отправкой сообщения
    limits = await limits_service.check_chat_limits(db, str(current_user.id))
    
    chat_obj = chat.get_chat(db=db, chat_id=chat_id)
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Сохраняем сообщение пользователя
    user_message = chat.add_message(
        db=db,
        chat_id=chat_id,
        role="user",
        content=message_in.content
    )

    # Проверяем, первое ли это сообщение
    messages_count = db.query(ChatMessage).filter(
        ChatMessage.chat_id == chat_id
    ).count()

    if messages_count == 1:  # Только что добавленное сообщение - первое
        try:
            await chat.update_chat_title_from_content(
                db=db,
                chat_id=chat_id,
                content=message_in.content
            )
        except Exception as e:
            print(f"Error updating chat title: {str(e)}")
            # Продолжаем выполнение даже если не удалось обновить название

    # Обновляем статистику использования
    await limits_service.update_usage(db, str(current_user.id), 'chat')

    try:
        # Получаем историю сообщений
        messages = []
        if chat_obj.is_memory_enabled:
            previous_messages = chat.get_chat_messages(db=db, chat_id=chat_id)
            messages = [{"role": msg.role, "content": msg.content} 
                       for msg in reversed(previous_messages)]
        else:
            messages = [{"role": "user", "content": message_in.content}]

        # Получаем системный промпт в зависимости от стиля бота
        system_prompt = anthropic_service.get_system_prompt_by_style(chat_obj.bot_style)
        
        # Отправляем запрос к Claude
        response = await anthropic_service.send_message(
            messages=messages,
            system=system_prompt
        )
        
        # Сохраняем ответ от Claude
        assistant_message = chat.add_message(
            db=db,
            chat_id=chat_id,
            role="assistant",
            content=response["content"][0]["text"]
        )
        
        return assistant_message

    except Exception as e:
        # В случае ошибки логируем её и возвращаем сообщение об ошибке
        print(f"Error in create_message: {str(e)}")  # для отладки
        error_message = chat.add_message(
            db=db,
            chat_id=chat_id,
            role="assistant",
            content=f"Извините, произошла ошибка при обработке сообщения. Пожалуйста, попробуйте позже."
        )
        return error_message

@router.get("/{chat_id}/messages/", response_model=List[ChatMessageInDB])
async def get_messages(
    *,
    db: Session = Depends(get_db),
    chat_id: UUID,
    limit: int = 50,
    before_id: UUID = None,
    current_user: User = Depends(get_current_user)
):
    """
    Получить сообщения чата с пагинацией.
    """
    chat_obj = chat.get_chat(db=db, chat_id=chat_id)
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return chat.get_chat_messages(
        db=db, 
        chat_id=chat_id,
        limit=limit,
        before_id=before_id
    )

