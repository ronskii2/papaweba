import httpx
import json
from datetime import datetime

# Базовый URL вашего API
BASE_URL = "http://localhost:8000/api/v1"

async def test_subscription_api():
    async with httpx.AsyncClient() as client:
        # 1. Регистрация админа
        admin_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "admin123",
            "full_name": "Admin User"
        }
        register_response = await client.post(f"{BASE_URL}/auth/register", json=admin_data)
        assert register_response.status_code == 200
        admin_token = register_response.json()["access_token"]

        # 2. Создание плана подписки
        plan_data = {
            "name": "premium_monthly",
            "display_name": "Premium Monthly",
            "period_type": "monthly",
            "price": "1190.00",
            "chat_requests_daily": 50,
            "image_generations_monthly": 100,
            "tool_cards_monthly": 500,
            "description": "Premium subscription with extended features"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        plan_response = await client.post(
            f"{BASE_URL}/subscriptions/plans/",
            json=plan_data,
            headers=headers
        )
        assert plan_response.status_code == 200
        plan = plan_response.json()
        print(f"Created plan: {plan['display_name']}")

        # 3. Получение списка планов
        plans_response = await client.get(f"{BASE_URL}/subscriptions/plans/")
        assert plans_response.status_code == 200
        plans = plans_response.json()
        print(f"Available plans: {len(plans)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_subscription_api())
