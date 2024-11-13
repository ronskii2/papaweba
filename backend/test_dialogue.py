import asyncio
import httpx
import uuid

BASE_URL = "http://134.122.79.143:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 60.0

async def test_dialogue():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # 1. Регистрация
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
        
        # 2. Логин
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

        # 3. Создание чата
        chat_data = {
            "title": "Test Chat",
            "bot_style": "friendly",
            "is_memory_enabled": True
        }
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/chats/",
            json=chat_data,
            headers=headers
        )
        chat_id = response.json()["id"]
        print("\nChat created:", response.json())

        # 4. Тестовый диалог

	# Проверяем лимиты перед отправкой сообщений
        print("\nChecking limits...")
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/chats/limits/",
            headers=headers
        )
        print("Limits:", response.json())

        messages = [
            "Отвечай только по делу: 1+2?",
            "Затем умножить на 4",
            "Теперь раздели на 2"
        ]

        for msg in messages:
            print(f"\nUser: {msg}")
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/chats/{chat_id}/messages/",
                json={"content": msg, "role": "user"},
                headers=headers
            )
            assistant_response = response.json()
            print(f"Assistant: {assistant_response['content']}")
	    # После отправки проверяем обновленные лимиты
            response = await client.get(
            f"{BASE_URL}{API_PREFIX}/chats/limits/",
            headers=headers
            )
            print("\nUpdated limits:", response.json())
            # Небольшая пауза между сообщениями
            await asyncio.sleep(1)


if __name__ == "__main__":
    print("Starting dialogue test...")
    asyncio.run(test_dialogue())
    print("\nDialogue test completed!")
