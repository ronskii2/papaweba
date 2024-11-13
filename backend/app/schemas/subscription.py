from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4
from decimal import Decimal

class SubscriptionPlanBase(BaseModel):
    name: str
    display_name: str
    period_type: str
    price: Decimal
    chat_requests_daily: int
    image_generations_monthly: int
    tool_cards_monthly: int
    description: Optional[str] = None
    is_trial: bool = False
    trial_duration_days: Optional[int] = None

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlanUpdate(SubscriptionPlanBase):
    is_active: Optional[bool] = None

class SubscriptionPlanInDB(SubscriptionPlanBase):
    id: UUID4
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserSubscriptionCreate(BaseModel):
    plan_id: UUID4
    payment_provider: Optional[str] = None
    payment_provider_subscription_id: Optional[str] = None

class UserSubscriptionUpdate(BaseModel):
    cancel_at_period_end: Optional[bool] = None
    status: Optional[str] = None

class UserSubscriptionInDB(BaseModel):
    id: UUID4
    user_id: UUID4
    plan_id: UUID4
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    payment_provider: Optional[str]
    payment_provider_subscription_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
