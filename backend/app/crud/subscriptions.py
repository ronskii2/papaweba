from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.subscription import SubscriptionPlan, UserSubscription
from uuid import UUID

class CRUDSubscription:
    @staticmethod
    def create_plan(
        db: Session,
        *,
        name: str,
        display_name: str,
        period_type: str,
        price: float,
        chat_requests_daily: int,
        image_generations_monthly: int,
        tool_cards_monthly: int,
        description: Optional[str] = None,
        is_trial: bool = False,
        trial_duration_days: Optional[int] = None
    ) -> SubscriptionPlan:
        db_obj = SubscriptionPlan(
            name=name,
            display_name=display_name,
            period_type=period_type,
            price=price,
            chat_requests_daily=chat_requests_daily,
            image_generations_monthly=image_generations_monthly,
            tool_cards_monthly=tool_cards_monthly,
            description=description,
            is_trial=is_trial,
            trial_duration_days=trial_duration_days
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_plan(db: Session, plan_id: UUID) -> Optional[SubscriptionPlan]:
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()

    @staticmethod
    def get_plan_by_name(db: Session, name: str) -> Optional[SubscriptionPlan]:
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.name == name).first()

    @staticmethod
    def get_all_active_plans(db: Session) -> List[SubscriptionPlan]:
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()

    @staticmethod
    def create_subscription(
        db: Session,
        *,
        user_id: UUID,
        plan_id: UUID,
        payment_provider: Optional[str] = None,
        payment_provider_subscription_id: Optional[str] = None,
        start_date: Optional[datetime] = None
    ) -> UserSubscription:
        if not start_date:
            start_date = datetime.utcnow()

        # Получаем план для определения периода
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        
        # Определяем дату окончания подписки
        if plan.period_type == "monthly":
            end_date = start_date + timedelta(days=30)
        elif plan.period_type == "yearly":
            end_date = start_date + timedelta(days=365)
        elif plan.is_trial:
            end_date = start_date + timedelta(days=plan.trial_duration_days or 7)
        else:
            end_date = start_date + timedelta(days=30)  # default to monthly

        db_obj = UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            current_period_start=start_date,
            current_period_end=end_date,
            payment_provider=payment_provider,
            payment_provider_subscription_id=payment_provider_subscription_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_active_subscription(db: Session, user_id: UUID) -> Optional[UserSubscription]:
        return db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == "active",
            UserSubscription.current_period_end > datetime.utcnow()
        ).first()

    @staticmethod
    def cancel_subscription(db: Session, subscription_id: UUID) -> Optional[UserSubscription]:
        db_obj = db.query(UserSubscription).filter(UserSubscription.id == subscription_id).first()
        if db_obj:
            db_obj.cancel_at_period_end = True
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def check_limits(db: Session, user_id: UUID) -> dict:
        """Проверяет лимиты пользователя на основе его подписки"""
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == "active",
            UserSubscription.current_period_end > datetime.utcnow()
        ).first()

        if not subscription:
            return {
                "has_active_subscription": False,
                "chat_requests_remaining": 0,
                "image_generations_remaining": 0,
                "tool_cards_remaining": 0
            }

        plan = subscription.plan
        # Здесь можно добавить логику подсчета использованных запросов
        return {
            "has_active_subscription": True,
            "chat_requests_remaining": plan.chat_requests_daily,
            "image_generations_remaining": plan.image_generations_monthly,
            "tool_cards_remaining": plan.tool_cards_monthly
        }

subscription = CRUDSubscription()
