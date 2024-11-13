from anthropic import Anthropic
from typing import Optional, Dict, Any, List
from app.core.config import settings

class AnthropicService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-haiku-20240307"

    def prepare_context(self, messages: List[Dict[str, str]], max_context: int = 2) -> List[Dict[str, str]]:
        """
        Подготовить контекст для отправки в Claude.
        Берем последние max_context пар сообщений (user + assistant) + текущее сообщение.
        """
        if len(messages) <= (max_context * 2 + 1):
            return messages
            
        # Берем только последние сообщения
        start_idx = -(max_context * 2 + 1)
        return messages[start_idx:]

    async def send_message(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Отправить сообщение в Claude API.
        """
        try:
            # Подготавливаем контекст
            context_messages = self.prepare_context(messages)
            
            # Формируем тело запроса
            request_body = {
                "messages": context_messages
            }
            
            if system:
                request_body["system"] = system

            # Отправляем запрос
            response = self.client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens,
                temperature=temperature,
                **request_body
            )

            return {
                "content": [{"text": response.content[-1].text}]
            }

        except Exception as e:
            raise ValueError(f"Failed to send message: {str(e)}")

    def get_system_prompt_by_style(self, style: str) -> str:
        """
        Получить системный промпт в зависимости от выбранного стиля.
        """
        style_prompts = {
            "friendly": "Ты дружелюбный и отзывчивый помощник. Используй неформальный стиль общения, будь позитивным и эмпатичным.",
            "professional": "Ты профессиональный ассистент. Используй формальный стиль общения, будь точным и информативным.",
            "concise": "Ты лаконичный помощник. Давай короткие, но полные ответы без лишних деталей.",
            "creative": "Ты креативный помощник. Используй образные выражения, метафоры и будь находчивым в ответах.",
            "standard": "Ты универсальный помощник. Адаптируй свой стиль под контекст разговора."
        }
        return style_prompts.get(style, style_prompts["standard"])

anthropic_service = AnthropicService()
