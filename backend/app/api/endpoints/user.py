from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user_settings import UserSettings, UserSettingsUpdate

router = APIRouter()

BOT_STYLES = {
    "standard": "Универсальный помощник с адаптивным стилем общения",
    "friendly": "Дружелюбный и неформальный стиль общения",
    "professional": "Формальный и деловой стиль общения",
    "concise": "Краткие и точные ответы без лишних слов",
    "creative": "Творческий подход с использованием метафор и образных выражений"
}

@router.get("/settings", response_model=UserSettings)
async def get_user_settings(
    current_user: User = Depends(get_current_user)
):
    """
    Получить текущие настройки пользователя
    """
    available_styles = [
        {"id": style_id, "name": style_id.capitalize(), "description": desc}
        for style_id, desc in BOT_STYLES.items()
    ]
    
    return {
        "default_bot_style": current_user.default_bot_style,
        "available_bot_styles": available_styles
    }

@router.patch("/settings", response_model=UserSettings)
async def update_user_settings(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    settings: UserSettingsUpdate
):
    """
    Обновить настройки пользователя
    """
    if settings.default_bot_style and settings.default_bot_style not in BOT_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid bot style. Available styles: {', '.join(BOT_STYLES.keys())}"
        )
    
    if settings.default_bot_style:
        current_user.default_bot_style = settings.default_bot_style
        db.commit()
    
    return await get_user_settings(current_user)
