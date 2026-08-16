from services.ai_provider import AIProvider
import json

class MockAIProvider(AIProvider):
    """Заглушка для тестирования. Возвращает предопределённый JSON."""
    def generate_structured_knowledge(self, prompt: str, schema: dict) -> dict:
        # Игнорируем prompt, возвращаем фиктивные данные
        fake_data = {
            "source_engine": "1JZ-GTE",
            "target_engine": "2JZ-GTE",
            "difficulty": 5,
            "difficulty_label": "Medium",
            "mounts_required": True,
            "wiring_required": True,
            "ecu_required": True,
            "cooling_upgrade": False,
            "driveshaft_modification": True,
            "compatible_transmissions": ["R154", "V160", "V161"]
        }
        return fake_data