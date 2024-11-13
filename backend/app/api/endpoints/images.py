from fastapi import Query
from datetime import datetime
from app.schemas.image import ImageGalleryResponse
import asyncio
from app.schemas.image import ImageCreate, ImageInDB, VALID_STYLES
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import aiohttp
from typing import Optional, List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from app.services.anthropic import anthropic_service
from app.services.limits import limits_service
from app.crud.images import image  
from app.models.user_images import UserImage 
import logging
import re
logger = logging.getLogger(__name__)




router = APIRouter()

class BFLClient:
    def __init__(self, api_key: str, base_url: str = "https://api.bfl.ml"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-Key": api_key,
            "Content-Type": "application/json"
        }

    def _get_dimensions(self, aspect_ratio: str):
        """
        Возвращает размеры изображения на основе соотношения сторон.
        Убедитесь, что и ширина, и высота кратны 32.
        """
        ratios = {
            "1:1": (1024, 1024),
            "16:9": (1408, 800),
            "9:16": (800, 1408),
            "4:5": (1024, 1280),
            "5:4": (1280, 1024),
            "3:2": (1440, 960),
            "2:3": (960, 1440)
        }
        return ratios.get(aspect_ratio, (1024, 1024))

    async def create_image(self, prompt: str, aspect_ratio: str = "1:1") -> Optional[bytes]:
        """
        Генерирует изображение с помощью BFL API и возвращает байты изображения.
        """
        try:
            logger.info(f"BFL: Starting image generation. Prompt: {prompt}, Aspect Ratio: {aspect_ratio}")
            width, height = self._get_dimensions(aspect_ratio)

            payload = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "steps": 40,
                "prompt_upsampling": False,
                "guidance": 2,
                "safety_tolerance": 2,
                "interval": 2,
                "output_format": "png"
            }

            logger.info(f"BFL: Using payload: {payload}")
            timeout = aiohttp.ClientTimeout(total=120)  # Увеличенный таймаут

            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Шаг 1: Отправка задачи на генерацию
                async with session.post(
                    f"{self.base_url}/v1/flux-dev",  # Правильный эндпоинт
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_text = await response.text()
                    logger.info(f"BFL: Initial response status: {response.status}, text: {response_text}")

                    if response.status != 200:
                        logger.error(f"BFL: Initial request failed: {response_text}")
                        raise HTTPException(status_code=500, detail="Initial request to image API failed.")

                    result = await response.json()
                    task_id = result.get("id")

                    if not task_id:
                        logger.error("BFL: No task ID in response")
                        raise HTTPException(status_code=500, detail="No task ID returned by image API.")

                    logger.info(f"BFL: Got task ID: {task_id}")

                    # Шаг 2: Проверка статуса задачи
                    max_attempts = 60
                    check_interval = 2 

                    for attempt in range(max_attempts):
                        logger.info(f"BFL: Checking status, attempt {attempt + 1}/{max_attempts}")

                        async with session.get(
                            f"{self.base_url}/v1/get_result",
                            params={"id": task_id},
                            headers=self.headers
                        ) as status_response:
                            status_text = await status_response.text()

                            if status_response.status != 200:
                                logger.warning(f"BFL: Status check failed, attempt {attempt + 1}, response: {status_text}")
                                await asyncio.sleep(check_interval)
                                continue

                            try:
                                status_data = await status_response.json()
                                current_status = status_data.get('status')
                                logger.info(f"BFL: Task status: {current_status}")

                                if current_status == "Ready" and status_data.get("result"):
                                    sample_url = status_data["result"].get("sample")
                                    if sample_url:
                                        try:
                                            # Шаг 3: Загрузка изображения по URL
                                            async with session.get(sample_url) as image_response:
                                                if image_response.status == 200:
                                                    image_bytes = await image_response.read()
                                                    logger.info("BFL: Image downloaded successfully")
                                                    return image_bytes
                                                else:
                                                    error_text = await image_response.text()
                                                    logger.error(f"BFL: Failed to download image: {error_text}")
                                                    raise HTTPException(status_code=500, detail="Failed to download image.")
                                        except Exception as e:
                                            logger.error(f"BFL: Error downloading image: {e}")
                                            raise HTTPException(status_code=500, detail="Error downloading image.")
                                    else:
                                        logger.error(f"BFL: No sample URL in result: {status_data}")
                                        raise HTTPException(status_code=500, detail="No image URL returned by API.")

                                elif current_status in ["Request Moderated", "Content Moderated"]:
                                    logger.warning(f"BFL: Content moderated for task {task_id}")
                                    raise HTTPException(status_code=400, detail="Content moderated by API.")

                                elif current_status == "Error":
                                    error_message = status_data.get('error', 'Unknown error')
                                    logger.error(f"BFL: Task failed with error: {error_message}")
                                    raise HTTPException(status_code=500, detail=f"Image generation failed: {error_message}")

                                elif current_status == "Pending":
                                    logger.info(f"BFL: Task {task_id} is still pending")
                                    await asyncio.sleep(check_interval)
                                    continue

                                else:
                                    logger.warning(f"BFL: Unknown status '{current_status}' for task {task_id}")
                                    await asyncio.sleep(check_interval)
                                    continue

                            except Exception as e:
                                logger.error(f"BFL: Error parsing status response: {e}")
                                await asyncio.sleep(check_interval)
                                continue

                    logger.error(f"BFL: Timed out waiting for image generation for task {task_id}")
                    raise HTTPException(status_code=500, detail="Timed out waiting for image generation.")

        except HTTPException as http_exc:
            raise http_exc  # Перепросите HTTPException без изменений
        except Exception as e:
            logger.error(f"BFL: Error in create_image: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error during image generation: {e}"
            )

@router.post("/generate/", response_model=ImageInDB)
async def generate_image(
    image_data: ImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Starting image generation for user {current_user.id}")
        logger.info(f"Request data: {image_data}")

        # Проверяем лимиты
        limits = await limits_service.check_chat_limits(db, str(current_user.id))
        if limits["remaining"] <= 0:
            raise HTTPException(400, "Daily generation limit exceeded")

        # Переводим промпт если нужно
        if not is_english(image_data.prompt):
            logger.info("Translating prompt to English")
            translation = await anthropic_service.send_message(
                messages=[{"role": "user", "content": f"В ответ пришли только перевод на английский: {image_data.prompt}"}],
                temperature=0.3
            )
            translated_prompt = translation["content"][0]["text"]
            logger.info(f"Translated prompt: {translated_prompt}")
        else:
            translated_prompt = image_data.prompt

        # Добавляем стиль в промпт если указан
        final_prompt = translated_prompt
        if image_data.style and image_data.style != "БЕЗ_СТИЛЯ":
            style_text = VALID_STYLES[image_data.style]
            final_prompt = f"{translated_prompt}, {style_text}"
            logger.info(f"Final prompt with style: {final_prompt}")

        # Генерируем изображение
        client = BFLClient(api_key=settings.BFL_API_KEY)
        image_url = await client.create_image(
            prompt=final_prompt,
            aspect_ratio=image_data.aspect_ratio
        )

        if not image_url:
            logger.error("Failed to generate image")
            raise HTTPException(500, "Failed to generate image")

        logger.info("Image generated successfully")

        # Сохраняем в БД
        db_obj = image.create(
            db,
            user_id=current_user.id,
            prompt=image_data.prompt,
            translated_prompt=final_prompt,
            image_url=image_url,
            aspect_ratio=image_data.aspect_ratio,
            style=image_data.style
        )

        # Обновляем использование
        await limits_service.update_usage(db, str(current_user.id), 'image')

        return db_obj

    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Error generating image: {str(e)}")

@router.get("/", response_model=List[ImageInDB])
async def get_user_images(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all user's images"""
    return image.get_user_images(db, current_user.id, skip, limit)

@router.delete("/{image_id}")
async def delete_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user's image"""
    if image.delete_image(db, image_id, current_user.id):
        return {"status": "success"}
    raise HTTPException(404, "Image not found")


def is_english(text: str) -> bool:
    try:
        # Проверяем, содержит ли текст русские буквы
        russian_pattern = re.compile('[а-яА-Я]')
        return not bool(russian_pattern.search(text))
    except Exception:
        return False

@router.get("/gallery/", response_model=ImageGalleryResponse)
async def get_user_gallery(
    page: int = Query(1, gt=0),
    limit: int = Query(20, gt=0, le=100),
    style: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить галерею изображений пользователя с фильтрами и пагинацией
    """
    offset = (page - 1) * limit
    
    images = image.get_user_images_filtered(
        db,
        user_id=current_user.id,
        style=style,
        start_date=start_date,
        end_date=end_date,
        search=search,
        skip=offset,
        limit=limit
    )
    
    total = image.count_user_images_filtered(
        db,
        user_id=current_user.id,
        style=style,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    return {
        "images": images,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.delete("/{image_id}", status_code=204)
async def delete_user_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить изображение пользователя
    """
    result = image.delete_image(db, image_id=image_id, user_id=current_user.id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Image not found or access denied"
        )
