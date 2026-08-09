import openai
from sqlalchemy import or_
from flask import current_app
from models import Article, Compatibility, Model, Brand

def ask_deepseek(question):
    """
    Отправляет вопрос в DeepSeek API с контекстом из базы знаний AUTOFORGE.
    Возвращает строку с ответом.
    """
    # 1. Собираем контекст из базы
    context = _build_context(question)

    # 2. Формируем системный промпт
    system_prompt = """Ты — эксперт по автомобильным свапам и модификациям, работаешь в платформе AUTOFORGE.
Твоя задача — помогать пользователям с выбором компонентов, объяснять совместимость и давать рекомендации на основе базы знаний AUTOFORGE.
Отвечай на русском языке, структурированно: сначала краткий ответ, затем список необходимых деталей или шагов.
Используй только информацию из предоставленного контекста. Если данных недостаточно, честно скажи об этом.
Никогда не выдумывай несуществующие детали или цены."""

    # 3. Собираем сообщения
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Контекст из базы AUTOFORGE:\n{context}\n\nВопрос пользователя: {question}"}
    ]

    # 4. Отправляем запрос в DeepSeek
    try:
        client = openai.OpenAI(
            api_key=current_app.config['DEEPSEEK_API_KEY'],
            base_url=current_app.config.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        current_app.logger.error(f"DeepSeek API error: {e}")
        return "Извините, произошла ошибка при обращении к ИИ. Попробуйте позже."

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
