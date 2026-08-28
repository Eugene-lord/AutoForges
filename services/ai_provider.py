import os
import json
import openai
from abc import ABC, abstractmethod
from gigachat import GigaChat

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
            return _extract_json(content)
        except Exception as e:
            print(f"DeepSeek error: {e}")
            raise


class GigaChatProvider(AIProvider):
    """Провайдер GigaChat (Сбер) с использованием официальной библиотеки."""
    def __init__(self, authorization_key=None, model="GigaChat"):
        self.authorization_key = authorization_key or os.environ.get("GIGACHAT_AUTHORIZATION_KEY")
        if not self.authorization_key:
            raise ValueError("GIGACHAT_AUTHORIZATION_KEY не задан")
        self.model = model
        # Используем библиотеку gigachat, передавая credentials (Authorization key)
        self.client = GigaChat(credentials=self.authorization_key, verify_ssl_certs=False)

    def generate_structured_knowledge(self, prompt: str, schema: dict) -> dict:
        system_prompt = (
            "Ты — автомобильный эксперт. Верни ответ строго в формате JSON, "
            "соответствующем следующей схеме:\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n"
            "Не добавляй лишних комментариев, только JSON."
        )
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()
            return _extract_json(content)
        except Exception as e:
            print(f"GigaChat error: {e}")
            raise


class FallbackProvider(AIProvider):
    """Провайдер с fallback: GigaChat -> DeepSeek -> Mock."""
    def __init__(self):
        self.providers = []
        # Пробуем GigaChat
        try:
            self.providers.append(GigaChatProvider())
        except Exception as e:
            print(f"GigaChat не инициализирован: {e}")
        # Пробуем DeepSeek
        try:
            self.providers.append(DeepSeekProvider())
        except Exception as e:
            print(f"DeepSeek не инициализирован: {e}")
        # Резервный Mock
        from services.mock_ai_provider import MockAIProvider
        self.providers.append(MockAIProvider())

    def generate_structured_knowledge(self, prompt: str, schema: dict) -> dict:
        for provider in self.providers:
            try:
                return provider.generate_structured_knowledge(prompt, schema)
            except Exception as e:
                print(f"Провайдер {provider.__class__.__name__} не сработал: {e}")
        raise RuntimeError("Все AI-провайдеры недоступны")


def _extract_json(content: str) -> dict:
    """Извлекает JSON из строки ответа."""
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)