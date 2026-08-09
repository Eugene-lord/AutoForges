from flask import Blueprint, render_template, request
from models import SwapProject, Model, Brand

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/')
def index():
    query = request.args.get('q', '').strip()
    projects = []
    models = []
    if query:
        # Поиск по проектам
        projects = SwapProject.query.filter(
            SwapProject.name.ilike(f'%{query}%'),
            SwapProject.is_public == True,
            SwapProject.is_approved == True
        ).all()
        # Поиск по автомобилям (Model + Brand)
        models = Model.query.join(Brand).filter(
            (Model.name.ilike(f'%{query}%')) | (Brand.name.ilike(f'%{query}%'))
        ).all()
    return render_template('search.html', query=query, projects=projects, models=models)
