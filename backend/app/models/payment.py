from datetime import datetime
from typing import Optional
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class Payment(Base):
    __tablename__ = 'payments'

    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    subscription_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('user_subscriptions.id'))
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default='RUB')
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_provider_payment_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Отношения
    user: Mapped[Optional["User"]] = relationship("User")
    subscription: Mapped[Optional["UserSubscription"]] = relationship("UserSubscription", back_populates="payments")
