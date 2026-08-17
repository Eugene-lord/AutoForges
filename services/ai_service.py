import openai
from sqlalchemy import or_
from flask import current_app
from models import Article, Compatibility, Model, Brand

def ask_deepseek(question):
    """
    Отправляет вопрос в DeepSeek API с контекстом из базы знаний AUTOMATCH.
    При недоступности DeepSeek возвращает заглушку через MockAIProvider.
    """
    # 1. Собираем контекст из базы (статьи, совместимости)
    context = _build_context(question)

    # 2. Формируем системный промпт
    system_prompt = """Ты — эксперт по автомобильным свапам и модификациям, работаешь в платформе AutoForge.
Твоя задача — помогать пользователям с выбором компонентов, объяснять совместимость и давать рекомендации на основе базы знаний AutoForge.
Отвечай на русском языке, структурированно: сначала краткий ответ, затем список необходимых деталей или шагов.
Используй только информацию из предоставленного контекста. Если данных недостаточно, честно скажи об этом.
Никогда не выдумывай несуществующие детали или цены."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Контекст из базы AutoForge:\n{context}\n\nВопрос пользователя: {question}"}
    ]

    # 3. Используем FallbackProvider (DeepSeek -> Mock)
    from services.ai_provider import FallbackProvider
    provider = FallbackProvider()
    try:
        # Пытаемся получить ответ от провайдера (структурированный не нужен, просто текст)
        schema = {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}
        result = provider.generate_structured_knowledge(
            prompt=question + "\nКонтекст:\n" + context,
            schema=schema
        )
        if not result or 'answer' not in result:
            return "ИИ-сервис временно недоступен. Попробуйте позже или воспользуйтесь конструктором свапов."
        return result['answer']
    except Exception as e:
        print(f"Ошибка при обращении к AI: {e}")
        return "ИИ-сервис временно недоступен. Вы можете воспользоваться конструктором свапов."

from sqlalchemy import or_

def _build_context(question):
    """Собирает релевантные данные из БД на основе вопроса пользователя."""
    query_lower = question.lower()
    context_parts = []

    # Ищем статьи по ключевым словам
    articles = Article.query.all()
    relevant_articles = []
    for art in articles:
        if any(word in query_lower for word in (art.title + ' ' + art.content + ' ' + (art.tags or '')).lower().split()):
            relevant_articles.append(art)
    if relevant_articles:
        context_parts.append("=== Статьи ===")
        for art in relevant_articles[:3]:
            context_parts.append(f"Заголовок: {art.title}\nСодержание: {art.content[:500]}...\n")

    # Ищем совместимости по названиям моделей/двигателей
    words = query_lower.split()
    if words:
        conditions = []
        for word in words:
            conditions.append(
                Model.name.ilike(f'%{word}%') | Brand.name.ilike(f'%{word}%')
            )
        models = Model.query.join(Brand).filter(or_(*conditions)).limit(5).all()
    else:
        models = []

    if models:
        context_parts.append("=== Совместимости ===")
        for model in models:
            comps = Compatibility.query.filter_by(vehicle_model_id=model.id).all()
            for comp in comps:
                context_parts.append(
                    f"Модель: {model.brand.name} {model.name} ({model.generation})\n"
                    f"Компонент типа '{comp.component_type}' ID {comp.component_id}: "
                    f"Статус: {comp.status}, Описание: {comp.description or 'нет'}, "
                    f"Стоимость: ${comp.estimated_cost or 0}, Сложность: {comp.difficulty or 0}/10\n"
                )

    if not context_parts:
        return "В базе знаний AUTOFORGE пока нет информации по вашему запросу."

    return '\n'.join(context_parts)
