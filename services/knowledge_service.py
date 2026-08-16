import json
from datetime import datetime
from services.ai_provider import DeepSeekProvider
from models import db, KnowledgeItem

# Простая схема для проверки JSON (можно расширить)
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "source_engine": {"type": "string"},
        "target_engine": {"type": "string"},
        "difficulty": {"type": "integer"},
        "difficulty_label": {"type": "string"},
        "mounts_required": {"type": "boolean"},
        "wiring_required": {"type": "boolean"},
        "ecu_required": {"type": "boolean"},
        "cooling_upgrade": {"type": "boolean"},
        "driveshaft_modification": {"type": "boolean"},
        "compatible_transmissions": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["source_engine", "target_engine", "difficulty", "difficulty_label"]
}

def classify_risk(data: dict) -> str:
    """
    Простая классификация риска на основе содержимого.
    Если есть флаги wiring_required, ecu_required или driveshaft_modification,
    считаем HIGH или MEDIUM. Для MVP можно возвращать MEDIUM по умолчанию.
    """
    if data.get("wiring_required") or data.get("ecu_required") or data.get("driveshaft_modification"):
        return "HIGH"
    elif data.get("mounts_required") or data.get("cooling_upgrade"):
        return "MEDIUM"
    return "LOW"

def generate_knowledge(prompt: str, knowledge_type: str = "swap") -> KnowledgeItem:
    """
    Генерирует структурированные знания через AI, сохраняет их в KnowledgeItem.
    Возвращает объект KnowledgeItem.
    """
    # Создаём экземпляр провайдера (DeepSeek)
    provider = DeepSeekProvider()  # ключ из окружения
    # Вызываем AI
    data = provider.generate_structured_knowledge(prompt, JSON_SCHEMA)
    # Классифицируем риск
    risk = classify_risk(data)
    # Сохраняем в БД
    item = KnowledgeItem(
        knowledge_type=knowledge_type,
        source='ai',
        confidence=0.7,          # пока фиксированно, можно улучшить
        risk_level=risk,
        status='AI_GENERATED',
        data_json=json.dumps(data, ensure_ascii=False),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(item)
    db.session.commit()
    return item