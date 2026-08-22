from flask import Blueprint, render_template
from models import Article

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/knowledge')

@knowledge_bp.route('/')
def index():
    categories = [row[0] for row in Article.query.with_entities(Article.category).distinct().all()]
    return render_template('knowledge_base.html', categories=categories)

@knowledge_bp.route('/category/<category>')
def category(category):
    articles = Article.query.filter_by(category=category).order_by(Article.created_at.desc()).all()
    title = f"Статьи по категории: {category} | AutoForge"
    description = f"База знаний AutoForge: статьи о свапах, компонентах и автомобилях в категории {category}."
    return render_template('article_list.html', category=category, articles=articles, title=title, description=description)

@knowledge_bp.route('/article/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    title = f"{article.title} | AutoForge"
    description = article.content[:160]
    return render_template('article_detail.html', article=article, title=title, description=description)