from pydantic import BaseModel
from typing import Optional

class UserSettingsUpdate(BaseModel):
    default_bot_style: Optional[str] = None

class UserSettings(BaseModel):
    default_bot_style: str
    available_bot_styles: list[dict[str, str]]  # список доступных стилей с описаниями

    class Config:
        from_attributes = True
