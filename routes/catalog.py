from flask import Blueprint, render_template
from services.catalog import get_all_brands, get_brand_by_id, get_models_by_brand, get_model_detail
from flask import Blueprint, render_template, request, url_for, redirect, flash
from models import Brand
catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/catalog')
def brand_list():
    page = request.args.get('page', 1, type=int)
    per_page = 9  # количество марок на странице
    pagination = Brand.query.order_by(Brand.name).paginate(page=page, per_page=per_page, error_out=False)
    brands = pagination.items
    title = "Каталог автомобилей | AutoForge"
    description = "Список марок и моделей автомобилей с возможностью просмотра совместимых двигателей и деталей."
    return render_template('catalog_brands.html', brands=brands, pagination=pagination, title=title, description=description)

@catalog_bp.route('/catalog/<int:brand_id>')
def model_list(brand_id):
    brand = get_brand_by_id(brand_id)
    models = get_models_by_brand(brand_id)
    return render_template('catalog_models.html', brand=brand, models=models)

@catalog_bp.route('/model/<int:model_id>')
def model_detail(model_id):
    model, engines = get_model_detail(model_id)
    title = f"{model.brand.name} {model.name} ({model.generation}) — характеристики и совместимые двигатели"
    description = f"Автомобиль {model.brand.name} {model.name} {model.generation}. Кузов: {model.body_type}. Годы выпуска: {model.year_start}-{model.year_end}. Смотрите совместимые двигатели и детали на AutoForge."
    return render_template('model_detail.html', model=model, engines=engines, title=title, description=description)
