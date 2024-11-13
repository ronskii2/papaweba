from enum import Enum
from pydantic import BaseModel
from openai import OpenAI
from typing import Tuple
from app.core.config import settings

# Шаг 1: Определение перечисления для эмодзи
class EmojiEnum(str, Enum):
    WORK = "💼"           # Работа
    ART = "🎨"            # Творчество
    HOME = "🏠"           # Жизнь
    HOBBY = "🎯"          # Хобби
    COMMUNICATION = "👥"  # Общение

# Шаг 2: Определение модели данных с использованием Enum
class ChatTitleResponse(BaseModel):
    title: str
    emoji: EmojiEnum

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Обновлено название модели

    async def generate_chat_title(self, content: str, max_length: int = 200) -> Tuple[str, str]:
        """
        Генерирует название чата и эмодзи на основе содержимого.
        Возвращает кортеж (title, emoji)
        """
        truncated_content = content[:max_length]
        
        # Шаг 3: Формируем сообщения для модели с указанием выбора эмодзи из заданных
        prompt = (
            "На основе этого содержимого чата сгенерируй короткое, осмысленное название "
            "(максимум 40 символов) и выбери ОДИН наиболее подходящий эмодзи из следующих категорий:\n"
            "- 💼 Работа\n"
            "- 🎨 Творчество\n"
            "- 🏠 Жизнь\n"
            "- 🎯 Хобби\n"
            "- 👥 Общение\n\n"
            f"Содержимое: \"{truncated_content}\"\n\n"
            "Верни ТОЛЬКО в таком формате JSON:\n"
            "{\n"
            '    "title": "название",\n'
            '    "emoji": "эмодзи"\n'
            "}"
        )
        
        messages = [
            {"role": "system", "content": "Ты генератор названий для чатов. Будь кратким и точным."},
            {"role": "user", "content": prompt}
        ]

        try:
            # Шаг 4: Запрос к OpenAI с использованием Structured Outputs
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=ChatTitleResponse,  # Указываем модель для парсинга ответа
                max_tokens=50
            )
            
            # Шаг 5: Извлечение структурированных данных
            parsed_response = completion.choices[0].message.parsed
            title = parsed_response.title
            emoji = parsed_response.emoji

            return title, emoji

        except Exception as e:
            print(f"Error generating chat title: {str(e)}")  # Для отладки
            return "Новый чат", "💭"

# Инициализация сервиса
openai_service = OpenAIService()
