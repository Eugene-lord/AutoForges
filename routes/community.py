from flask import Blueprint, render_template
from models import SwapProject

community_bp = Blueprint('community', __name__, url_prefix='/community')

@community_bp.route('/')
def index():
    # Публичные одобренные проекты, сортировка по дате создания
    projects = SwapProject.query.filter_by(is_public=True, is_approved=True)\
                                .order_by(SwapProject.created_at.desc()).all()
    return render_template('community.html', projects=projects)
