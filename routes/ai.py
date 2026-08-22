from flask import Blueprint, render_template, request
from services.ai_service import ask_deepseek
from extensions import limiter

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    question = None
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            answer = ask_deepseek(question)
    title = "ИИ-помощник | AutoForge"
    description = "Задайте вопрос об автомобильных свапах, совместимости деталей и модификациях. ИИ-помощник AutoForge."
    return render_template('ai_assistant.html', answer=answer, question=question, title=title, description=description)
