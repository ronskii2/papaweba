import httpx
import asyncio
import uuid
from typing import Dict

BASE_URL = "http://134.122.79.143:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 60.0

async def test_chat_api():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # 1. Регистрация пользователя
        unique_id = str(uuid.uuid4())[:8]
        register_data = {
            "email": f"test_{unique_id}@example.com",
            "username": f"testuser_{unique_id}",
            "password": "testpass123",
            "full_name": "Test User"
        }
        print(f"\nRegister user: {register_data['email']}")
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/register",
            json=register_data
        )
        print("Register response:", response.status_code, response.json())
        user_id = response.json()["id"]

        # 2. Логин
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        print("\nLogin")
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print("Login response:", response.status_code)
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        try:
            # 3. Создание папки чатов
            folder_data = {
                "name": "Test Folder",
                "emoji": "📁"
            }
            print("\nCreate chat folder")
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/chats/folders/",
                json=folder_data,
                headers=headers
            )
            print("Create folder response:", response.status_code)
            folder = response.json()
            folder_id = folder["id"]
            print("Folder created:", folder)

            # 4. Создание чата
            chat_data = {
                "title": "Test Chat",
                "folder_id": folder_id,
                "bot_style": "friendly",
                "is_memory_enabled": True
            }
            print("\nCreate chat")
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/chats/",
                json=chat_data,
                headers=headers
            )
            print("Create chat response:", response.status_code)
            chat_obj = response.json()
            chat_id = chat_obj["id"]
            print("Chat created:", chat_obj)

            # 5. Отправка сообщения
            message_data = {
                "content": "Hello, AI!",
                "role": "user"
            }
            print("\nSend message")
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/chats/{chat_id}/messages/",
                json=message_data,
                headers=headers
            )
            print("Send message response:", response.status_code)
            message = response.json()
            print("Message sent:", message)

            # 6. Получение сообщений
            print("\nGet messages")
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/chats/{chat_id}/messages/",
                headers=headers
            )
            print("Get messages response:", response.status_code)
            messages = response.json()
            print(f"Got {len(messages)} messages")

        except Exception as e:
            print(f"Error during test: {str(e)}")
            raise

if __name__ == "__main__":
    print("Starting chat API test...")
    asyncio.run(test_chat_api())
    print("\nChat API test completed!")
