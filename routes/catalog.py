from flask import Blueprint, render_template
from services.catalog import get_all_brands, get_brand_by_id, get_models_by_brand, get_model_detail

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/catalog')
def brand_list():
    brands = get_all_brands()
    return render_template('catalog_brands.html', brands=brands)

@catalog_bp.route('/catalog/<int:brand_id>')
def model_list(brand_id):
    brand = get_brand_by_id(brand_id)
    models = get_models_by_brand(brand_id)
    return render_template('catalog_models.html', brand=brand, models=models)

@catalog_bp.route('/model/<int:model_id>')
def model_detail(model_id):
    model, engines = get_model_detail(model_id)
    return render_template('model_detail.html', model=model, engines=engines)
