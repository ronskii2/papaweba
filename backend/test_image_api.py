import httpx
import asyncio
import uuid
from typing import Dict

BASE_URL = "http://134.122.79.143:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 120.0

async def test_image_api():
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

        try:
            # 3. Генерация изображения
            image_data = {
                "prompt": "красивый закат на море",
                "style": "РЕАЛИЗМ",
                "aspect_ratio": "16:9"
            }
            print("\nTesting image generation...")
            print(f"Request data: {image_data}")
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/images/generate/",
                json=image_data,
                headers=headers,
                timeout=60.0
            )
            print(f"Response headers: {response.headers}")
            print(f"Response content: {response.text}")
            print("Generate image response:", response.status_code)
            if response.status_code != 200:
                print("Error response:", response.text)
            else:
                image = response.json()
                print("Image generated:", image["id"])

                # 4. Получение списка изображений
                print("\nGetting user images...")
                response = await client.get(
                    f"{BASE_URL}{API_PREFIX}/images/",
                    headers=headers
                )
                print("Get images response:", response.status_code)
                if response.status_code == 200:
                    images = response.json()
                    print(f"User has {len(images)} images")

                    # 5. Удаление изображения
                    if images:
                        print("\nDeleting image...")
                        response = await client.delete(
                            f"{BASE_URL}{API_PREFIX}/images/{image['id']}",
                            headers=headers
                        )
                        print("Delete image response:", response.status_code)

        except Exception as e:
            print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    print("Starting image API test...")
    asyncio.run(test_image_api())
    print("\nImage API test completed!")
