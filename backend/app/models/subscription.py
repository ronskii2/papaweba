from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, String, Integer, ForeignKey, Text, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    chat_requests_daily: Mapped[int] = mapped_column(Integer, nullable=False)
    image_generations_monthly: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_cards_monthly: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False)
    trial_duration_days: Mapped[Optional[int]] = mapped_column(Integer) 


    # Отношения
    subscriptions: Mapped[List["UserSubscription"]] = relationship("UserSubscription", back_populates="plan")

class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey('subscription_plans.id'), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_provider: Mapped[Optional[str]] = mapped_column(String(50))
    payment_provider_subscription_id: Mapped[Optional[str]] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="subscription")
