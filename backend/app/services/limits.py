from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.chat import ChatMessage
from app.models.subscription import UserSubscription, SubscriptionPlan
from app.models.tool_usage import ToolUsage

class LimitsService:
    @staticmethod
    async def check_chat_limits(
        db: Session,
        user_id: str,
        throw_exception: bool = True
    ) -> Dict[str, any]:
        """
        Проверяет лимиты чата для пользователя.
        Возвращает dict с информацией о лимитах и их использовании.
        """
        # Получаем активную подписку
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == "active",
            UserSubscription.current_period_end > datetime.utcnow()
        ).first()

        if not subscription:
            # Бесплатный план
            daily_limit = 10  # Бесплатные сообщения в день
        else:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == subscription.plan_id
            ).first()
            daily_limit = plan.chat_requests_daily

        # Считаем использованные сообщения за сегодня
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_today = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.chat.has(user_id=user_id),
            ChatMessage.role == "user",
            ChatMessage.created_at >= today_start
        ).scalar()

        remaining = max(0, daily_limit - messages_today)
        
        if remaining == 0 and throw_exception:
            raise ValueError("Daily message limit exceeded")

        return {
            "daily_limit": daily_limit,
            "messages_today": messages_today,
            "remaining": remaining,
            "reset_at": (today_start + timedelta(days=1)).isoformat()
        }

    @staticmethod
    async def update_usage(
        db: Session,
        user_id: str,
        usage_type: str,
        amount: int = 1
    ):
        """
        Обновляет статистику использования.
        usage_type: 'chat', 'image', 'tool'
        """
        # Здесь можно добавить логику для записи статистики
        pass

limits_service = LimitsService()
