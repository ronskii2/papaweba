from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.subscription import subscription
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanInDB,
    UserSubscriptionCreate,
    UserSubscriptionInDB
)
from app.models.user import User
from app.core.auth import get_current_user, get_current_active_user, get_current_admin_user

router = APIRouter()

@router.post("/plans/", response_model=SubscriptionPlanInDB)
async def create_subscription_plan(
    *,
    db: Session = Depends(get_db),
    plan_in: SubscriptionPlanCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create new subscription plan (admin only).
    """
    return subscription.create_plan(db=db, **plan_in.dict())

@router.get("/plans/", response_model=List[SubscriptionPlanInDB])
async def list_subscription_plans(
    db: Session = Depends(get_db)
):
    """
    List all active subscription plans.
    """
    plans = subscription.get_all_active_plans(db=db)
    return plans

@router.post("/subscribe/", response_model=UserSubscriptionInDB)
async def create_subscription(
    subscription_in: UserSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Subscribe current user to a plan.
    """
    # Check if user already has active subscription
    active_sub = subscription.get_active_subscription(db=db, user_id=current_user.id)
    if active_sub:
        raise HTTPException(
            status_code=400,
            detail="User already has active subscription"
        )
    
    # Verify plan exists and is active
    plan = subscription.get_plan(db=db, plan_id=subscription_in.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found or inactive"
        )
    
    return subscription.create_subscription(
        db=db,
        user_id=current_user.id,
        **subscription_in.dict()
    )

@router.get("/my-subscription/", response_model=UserSubscriptionInDB)
async def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's active subscription.
    """
    active_sub = subscription.get_active_subscription(db=db, user_id=current_user.id)
    if not active_sub:
        raise HTTPException(
            status_code=404,
            detail="No active subscription found"
        )
    return active_sub

@router.post("/my-subscription/cancel/", response_model=UserSubscriptionInDB)
async def cancel_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel current user's subscription (will be active until period ends).
    """
    active_sub = subscription.get_active_subscription(db=db, user_id=current_user.id)
    if not active_sub:
        raise HTTPException(
            status_code=404,
            detail="No active subscription found"
        )
    
    return subscription.cancel_subscription(db=db, subscription_id=active_sub.id)

@router.get("/my-limits/", response_model=dict)
async def get_my_limits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's subscription limits.
    """
    return subscription.check_limits(db=db, user_id=current_user.id)
