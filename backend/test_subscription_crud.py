from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.crud.users import user
from app.crud.subscriptions import subscription
from datetime import datetime
import uuid

# Загружаем переменные окружения
load_dotenv()

def test_subscription_operations():
    db = SessionLocal()
    try:
        # 1. Создаем тестовый план подписки
        plan = subscription.create_plan(
            db,
            name="premium_monthly",
            display_name="Premium Monthly",
            period_type="monthly",
            price=1190.0,
            chat_requests_daily=50,
            image_generations_monthly=100,
            tool_cards_monthly=500,
            description="Premium subscription with extended features"
        )
        print(f"Created subscription plan: {plan.display_name}")

        # 2. Создаем тестового пользователя
        test_user = user.create(
            db,
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            username=f"testuser_{uuid.uuid4().hex[:8]}",
            password="testpassword123",
            full_name="Test User"
        )
        print(f"Created test user: {test_user.username}")

        # 3. Создаем подписку для пользователя
        user_subscription = subscription.create_subscription(
            db,
            user_id=test_user.id,
            plan_id=plan.id,
            payment_provider="stripe",
            payment_provider_subscription_id="sub_123"
        )
        print(f"Created user subscription, active until: {user_subscription.current_period_end}")

        # 4. Проверяем активную подписку
        active_sub = subscription.get_active_subscription(db, test_user.id)
        print(f"Found active subscription: {'Yes' if active_sub else 'No'}")

        # 5. Проверяем лимиты
        limits = subscription.check_limits(db, test_user.id)
        print(f"Subscription limits: {limits}")

        # 6. Отменяем подписку
        cancelled_sub = subscription.cancel_subscription(db, user_subscription.id)
        print(f"Subscription cancelled (will end at period end): {'Yes' if cancelled_sub.cancel_at_period_end else 'No'}")

    finally:
        db.close()

if __name__ == "__main__":
    print("Starting subscription CRUD operations test...")
    test_subscription_operations()
    print("Subscription CRUD operations test completed!")
