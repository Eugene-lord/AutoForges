from flask import Blueprint, render_template
from models import SwapProject

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    popular_projects = SwapProject.query.filter_by(is_public=True, is_approved=True)\
                                        .order_by(SwapProject.created_at.desc()).limit(3).all()
    title = "AutoForge — платформа для подбора совместимых деталей и свапов"
    description = "Соберите свой идеальный автомобиль: проверьте совместимость двигателей, КПП, подвески и других компонентов. AI-помощник и база знаний по свапам."
    return render_template('index.html', popular_projects=popular_projects, title=title, description=description)