from models import Brand, Model, Engine

def get_all_brands():
    return Brand.query.order_by(Brand.name).all()

def get_brand_by_id(brand_id):
    return Brand.query.get_or_404(brand_id)

def get_models_by_brand(brand_id):
    return Model.query.filter_by(brand_id=brand_id).order_by(Model.name).all()

def get_model_detail(model_id):
    model = Model.query.get_or_404(model_id)
    engines = model.engines.all()
    return model, engines
