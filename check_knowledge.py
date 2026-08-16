from app import create_app
from models import KnowledgeItem

app = create_app()
with app.app_context():
    items = KnowledgeItem.query.all()
    if not items:
        print("Записей не найдено.")
    for item in items:
        print(f"ID: {item.id}, Тип: {item.knowledge_type}, Риск: {item.risk_level}, Статус: {item.status}")
        print(item.data_json[:200])
        print('---')