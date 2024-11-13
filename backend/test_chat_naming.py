import asyncio
import httpx
import uuid
from typing import Dict

BASE_URL = "http://134.122.79.143:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 60.0

async def test_chat_naming():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Регистрация и аутентификация
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

        # Создаем чат
        chat_data = {
            "title": "New Chat"  # Временное название
        }
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/chats/",
            json=chat_data,
            headers=headers
        )
        chat = response.json()
        chat_id = chat["id"]
        print("\nInitial chat:", chat)

        # Отправляем первое сообщение
        message_data = {
            "content": "Можешь ли помочь мне написать бизнес-предложение по новому экологически чистому упаковочному решению?",
            "role": "user"
        }
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/chats/{chat_id}/messages/",
            json=message_data,
            headers=headers
        )
        print(f"response: {response}")
        print(f"\nMessage response status: {response.status_code}")
        print("\nMessage sent, checking updated chat...")

        # Получаем обновленный чат
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/chats/{chat_id}",
            headers=headers
        )
        updated_chat = response.json()
        print("\nUpdated chat title and emoji:", {
            "title": updated_chat["title"],
            "emoji": updated_chat.get("emoji", "No emoji")
        })

if __name__ == "__main__":
    print("Starting chat naming test...")
    asyncio.run(test_chat_naming())
    print("\nChat naming test completed!")
