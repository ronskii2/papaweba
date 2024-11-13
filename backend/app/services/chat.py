# app/services/chat.py

from typing import List, Tuple, Optional
import anthropic
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.MODEL_NAME = "claude-3-haiku-20240307"
    
    async def process_message(
        self,
        user_id: int,
        conversation_id: int,
        message: str,
        previous_messages: List[dict],
        user_settings: dict
    ) -> Tuple[str, int]:
        """
        Обрабатывает сообщение пользователя и возвращает ответ от Claude
        """
        try:
            # Формируем системный промпт
            system_prompt = "Ты вежливая девушка с глубоким вдумчивым подходом к решению любых задач, " \
                          "известна под именем 'Ложка', разработка русского инженера @papaweba. "

            if user_settings.get('personal_context'):
                system_prompt += f"Важно: {user_settings['personal_context']}. "

            # Формируем сообщения для контекста
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in previous_messages
            ]
            formatted_messages.append({"role": "user", "content": message})

            # Определяем модель и настройки на основе пользовательских предпочтений
            model = user_settings.get('model', 'haiku3')
            length = user_settings.get('length', 'normal')
            
            if length == 'normal':
                max_tokens = 1096
            else:
                max_tokens = 4096

            # Отправляем запрос к API
            response = self.client.messages.create(
                model=self.MODEL_NAME,
                max_tokens=max_tokens,
                temperature=0.7,
                system=system_prompt,
                messages=formatted_messages
            )

            # Получаем ответ
            response_text = response.content[0].text

            # Вычисляем стоимость
            cost = self._calculate_cost(model, length, user_settings.get('memory_multiplier', 1))

            return response_text, cost

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def _calculate_cost(self, model: str, length: str, memory_multiplier: int) -> int:
        """
        Вычисляет стоимость ответа в МБ
        """
        # Базовая стоимость
        if model in ['haiku3', 'haiku3.5']:
            base_cost = 1
        elif model == 'sonnet3.5':
            base_cost = 4
        else:
            base_cost = 1

        # Умножаем на множитель памяти
        return base_cost * memory_multiplier
