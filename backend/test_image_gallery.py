import httpx
import asyncio
import uuid
from datetime import datetime, timedelta

BASE_URL = "http://134.122.79.143:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 120.0

async def test_image_gallery():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Регистрация и логин (такой же как в test_image_api.py)
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

        # Тест галереи
        print("\nTesting image gallery...")
        
        # 1. Базовый запрос галереи
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/images/gallery/",
            headers=headers
        )
        print(f"Gallery response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total images: {data['total']}")
            print(f"Current page: {data['page']}/{data['pages']}")
        
        # 2. Тест фильтров
        filters = {
            "style": "РЕАЛИЗМ",
            "start_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "search": "закат"
        }
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/images/gallery/",
            params=filters,
            headers=headers
        )
        print(f"\nFiltered gallery response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Filtered total: {data['total']}")

if __name__ == "__main__":
    print("Starting image gallery test...")
    asyncio.run(test_image_gallery())
    print("\nImage gallery test completed!")
