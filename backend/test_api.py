import httpx
import asyncio
import uuid
from typing import Dict

BASE_URL = "http://134.122.79.143:8000"
API_PREFIX = "/api/v1"

async def test_api():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test API health
        print("\nChecking API health...")
        response = await client.get(f"{BASE_URL}/health")
        print("Health check response:", response.status_code, response.text)

        # 1. Регистрация пользователя
        unique_id = str(uuid.uuid4())[:8]
        register_data = {
            "email": f"test_{unique_id}@example.com",
            "username": f"testuser_{unique_id}",
            "password": "testpass123",
            "full_name": "Test User"
        }
        print(f"\nTrying to register user: {register_data['email']}")
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/register",
            json=register_data
        )
        print("Register response:", response.status_code, response.json())
        user_id = response.json()["id"]
	# Make user admin (temporary, for testing)
        async def make_user_admin(user_id: str):
            async with httpx.AsyncClient() as admin_client:
                # Прямой SQL запрос через API (в реальном приложении сделать безопаснее)
                response = await admin_client.post(
                    f"{BASE_URL}{API_PREFIX}/auth/make_admin",
		    params={"user_id": user_id} 
                )
                print("Make admin response:", response.status_code, response.text)

        await make_user_admin(user_id)
        # 2. Логин
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        print(f"\nTrying to login as: {login_data['username']}")
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print("Login response:", response.status_code)
        token_data = response.json()
        print("Token data:", token_data)
        
        # Правильный формат заголовка Authorization
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}"
        }
        print("Auth header:", headers)

        try:
            # 3. Создание плана подписки
            plan_data = {
                "name": f"premium_monthly_{unique_id}",
                "display_name": "Premium Monthly",
                "period_type": "monthly",
                "price": 1190.00,
                "chat_requests_daily": 50,
                "image_generations_monthly": 100,
                "tool_cards_monthly": 500,
                "description": "Premium subscription with extended features"
            }
            print("\nCreating subscription plan...")
            print("Request URL:", f"{BASE_URL}{API_PREFIX}/subscriptions/plans/")
            print("Request headers:", headers)
            print("Request data:", plan_data)
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/subscriptions/plans/",
                json=plan_data,
                headers=headers
            )
            print("Create plan response:", response.status_code)
            print("Response content:", response.text)
            
            if response.status_code == 200:
                plan_response = response.json()
                plan_id = plan_response["id"]
                print("Plan created with ID:", plan_id)

                # 4. Подписка на план
                subscription_data = {
                    "plan_id": plan_id,
                    "payment_provider": "test_provider",
                    "payment_provider_subscription_id": "test_sub_123"
                }
                print("\nSubscribing to plan...")
                response = await client.post(
                    f"{BASE_URL}{API_PREFIX}/subscriptions/subscribe/",
                    json=subscription_data,
                    headers=headers
                )
                print("Subscribe response:", response.status_code, response.text)
            else:
                print("Failed to create plan, skipping subscription test")

        except Exception as e:
            print(f"Error during test: {str(e)}")
            raise

if __name__ == "__main__":
    print("Starting API test...")
    asyncio.run(test_api())
    print("\nAPI test completed!")
