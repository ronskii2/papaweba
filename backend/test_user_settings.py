import asyncio
import httpx
import uuid

BASE_URL = "http://134.122.79.143:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 60.0

async def test_user_settings():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Регистрация
        unique_id = str(uuid.uuid4())[:8]
        register_data = {
            "email": f"test_{unique_id}@example.com",
            "username": f"testuser_{unique_id}",
            "password": "testpass123",
            "full_name": "Test User"
        }
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/register",
            json=register_data
        )
        print("Register response:", response.status_code)
        
        # Логин
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Получаем текущие настройки
        print("\nGetting current settings...")
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/users/settings",
            headers=headers
        )
        print("Current settings:", response.json())

        # Обновляем настройки
        print("\nUpdating settings...")
        update_data = {
            "default_bot_style": "friendly"
        }
        response = await client.patch(
            f"{BASE_URL}{API_PREFIX}/users/settings",
            json=update_data,
            headers=headers
        )
        print("Update response:", response.json())

        # Создаем чат с обновленным стилем по умолчанию
        print("\nCreating chat with default style...")
        chat_data = {
            "title": "Test Chat"
        }
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/chats/",
            json=chat_data,
            headers=headers
        )
        chat = response.json()
        print("Created chat:", chat)

if __name__ == "__main__":
    print("Starting user settings test...")
    asyncio.run(test_user_settings())
    print("\nUser settings test completed!")
