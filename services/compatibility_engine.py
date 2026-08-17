import json
from datetime import datetime
from models import db, Swap
from services.mock_ai_provider import MockAIProvider

SWAP_SCHEMA = {
    "type": "object",
    "properties": {
        "difficulty": {"type": "integer"},
        "required_modifications": {"type": "array", "items": {"type": "string"}},
        "required_parts": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "string"},
        "compatible_transmissions": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["difficulty", "required_modifications", "required_parts"]
}

def find_swap_in_db(source_vehicle_model_id, source_component_type, source_component_id,
                    target_component_type, target_component_id):
    return Swap.query.filter_by(
        source_vehicle_model_id=source_vehicle_model_id,
        source_component_type=source_component_type,
        source_component_id=source_component_id,
        target_component_type=target_component_type,
        target_component_id=target_component_id
    ).first()

def generate_swap_and_save(source_vehicle_model_id, source_component_type, source_component_id,
                           target_component_type, target_component_id):
    from services.ai_provider import FallbackProvider
    provider = FallbackProvider()
    prompt = f"Опиши свап из {source_component_type} id={source_component_id} в {target_component_type} id={target_component_id} для автомобиля id={source_vehicle_model_id}"
    data = provider.generate_structured_knowledge(prompt, SWAP_SCHEMA)

    difficulty = int(data.get('difficulty', 5))
    required_mods = data.get('required_modifications', [])
    required_parts = data.get('required_parts', [])
    notes = data.get('notes', '')

    swap = Swap(
        source_vehicle_model_id=source_vehicle_model_id,
        source_component_type=source_component_type,
        source_component_id=source_component_id,
        target_component_type=target_component_type,
        target_component_id=target_component_id,
        difficulty=difficulty,
        required_modifications=json.dumps(required_mods, ensure_ascii=False),
        required_parts=json.dumps(required_parts, ensure_ascii=False),
        notes=notes,
        status='AI_GENERATED',
        source='ai',
        confidence=0.7,
        risk_level='MEDIUM',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(swap)
    db.session.commit()
    return swap

def get_or_create_swap(source_vehicle_model_id, source_component_type, source_component_id,
                       target_component_type, target_component_id):
    existing = find_swap_in_db(source_vehicle_model_id, source_component_type, source_component_id,
                               target_component_type, target_component_id)
    if existing:
        return existing, False
    swap = generate_swap_and_save(source_vehicle_model_id, source_component_type, source_component_id,
                                  target_component_type, target_component_id)
    return swap, True