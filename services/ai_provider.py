import os
import json
import openai
from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Абстрактный базовый класс для AI-провайдеров."""
    @abstractmethod
    def generate_structured_knowledge(self, prompt: str, schema: dict) -> dict:
        """Возвращает структурированный ответ в виде словаря согласно schema."""
        pass


class DeepSeekProvider(AIProvider):
    """Провайдер DeepSeek (совместим с OpenAI SDK)."""
    def __init__(self, api_key=None, base_url="https://api.deepseek.com/v1", model="deepseek-chat"):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.model = model
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY не задан")

    def generate_structured_knowledge(self, prompt: str, schema: dict) -> dict:
        # Формируем системный промпт с требованием вернуть JSON по схеме
        system_prompt = (
            "Ты — автомобильный эксперт. Верни ответ строго в формате JSON, "
            "соответствующем следующей схеме:\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n"
            "Не добавляй лишних комментариев, только JSON."
        )
        try:
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500,
                stream=False
            )
            content = response.choices[0].message.content.strip()
            # Попытка извлечь JSON из ответа
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            return data
        except Exception as e:
            print(f"DeepSeek error: {e}")
            raise

class FallbackProvider(AIProvider):
    """Провайдер с fallback: сначала DeepSeek, при ошибке — Mock."""
    def __init__(self):
        self.primary = None
        try:
            self.primary = DeepSeekProvider()
        except Exception as e:
            print(f"DeepSeek не инициализирован: {e}")
        # Резервный провайдер
        from services.mock_ai_provider import MockAIProvider
        self.fallback = MockAIProvider()

    def generate_structured_knowledge(self, prompt: str, schema: dict) -> dict:
        if self.primary:
            try:
                return self.primary.generate_structured_knowledge(prompt, schema)
            except Exception as e:
                print(f"Ошибка DeepSeek, переключаюсь на Mock: {e}")
        return self.fallback.generate_structured_knowledge(prompt, schema)