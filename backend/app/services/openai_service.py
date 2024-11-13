from pydantic import BaseModel
from openai import OpenAI
from typing import Tuple, Literal
from app.core.config import settings

class ChatTitleResponse(BaseModel):
    title: str
    emoji: Literal["💼", "🎨", "🏠", "🎯", "👥"]  # строгое ограничение эмодзи

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"

    async def generate_chat_title(self, content: str, max_length: int = 200) -> Tuple[str, str]:
        """
        Генерирует название чата и эмодзи на основе содержимого.
        Возвращает кортеж (title, emoji)
        """
        try:
            truncated_content = content[:max_length]
            
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты генератор названий для чатов. На основе содержимого генерируй короткое название (до 40 символов) и подбирай один эмодзи из списка: 💼 (работа/бизнес), 🎨 (творчество), 🏠 (дом/быт), 🎯 (хобби/развлечения), 👥 (общение/отношения). Используй русский язык для названия."},
                    {"role": "user", "content": truncated_content}
                ],
                response_format=ChatTitleResponse
            )
            
            result = completion.choices[0].message.parsed
            return result.title, result.emoji

        except Exception as e:
            print(f"Error generating chat title: {str(e)}")
            return "Новый чат", "💭"

openai_service = OpenAIService()
