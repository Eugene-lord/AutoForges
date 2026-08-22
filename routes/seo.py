from flask import Blueprint, Response, url_for, render_template
from models import Model, Article

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/robots.txt')
def robots():
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin",
        "Disallow: /profile",
        "Sitemap: " + url_for('seo.sitemap', _external=True)
    ]
    return Response("\n".join(lines), mimetype='text/plain')

@seo_bp.route('/sitemap.xml')
def sitemap():
    pages = []
    # Главная
    pages.append({
        'loc': url_for('main.index', _external=True),
        'priority': '1.0'
    })
    # Каталог
    pages.append({
        'loc': url_for('catalog.brand_list', _external=True),
        'priority': '0.8'
    })
    # Страницы моделей
    models = Model.query.all()
    for model in models:
        pages.append({
            'loc': url_for('catalog.model_detail', model_id=model.id, _external=True),
            'priority': '0.7'
        })
    # Статьи
    articles = Article.query.all()
    for article in articles:
        pages.append({
            'loc': url_for('knowledge.article_detail', article_id=article.id, _external=True),
            'priority': '0.5'
        })
    # Сообщество
    pages.append({
        'loc': url_for('community.index', _external=True),
        'priority': '0.6'
    })
    # AI-помощник
    pages.append({
        'loc': url_for('ai.index', _external=True),
        'priority': '0.4'
    })

    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for page in pages:
        xml_content.append('<url>')
        xml_content.append(f"<loc>{page['loc']}</loc>")
        xml_content.append(f"<priority>{page['priority']}</priority>")
        xml_content.append('</url>')
    xml_content.append('</urlset>')

    return Response("\n".join(xml_content), mimetype='application/xml')