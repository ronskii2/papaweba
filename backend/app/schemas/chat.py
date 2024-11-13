from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, UUID4

class ChatFolderBase(BaseModel):
    name: str
    emoji: Optional[str] = None

class ChatFolderCreate(ChatFolderBase):
    pass

class ChatFolderUpdate(ChatFolderBase):
    order_index: Optional[int] = None

class ChatFolderInDB(ChatFolderBase):
    id: UUID4
    user_id: UUID4
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    content: str
    role: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageInDB(ChatMessageBase):
    id: UUID4
    chat_id: UUID4
    tokens_used: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    title: Optional[str] = None
    bot_style: Optional[str] = "standard"
    is_memory_enabled: bool = True

class ChatCreate(ChatBase):
    folder_id: Optional[UUID4] = None
    is_memory_enabled: bool = True

class ChatUpdate(ChatBase):
    folder_id: Optional[UUID4] = None

class ChatInDB(ChatBase):
    id: UUID4
    user_id: UUID4
    folder_id: Optional[UUID4]
    auto_title_number: int
    created_at: datetime
    messages: Optional[List[ChatMessageInDB]]

    class Config:
        from_attributes = True
