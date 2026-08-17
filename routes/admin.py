from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import (db, Brand, Model, Engine, Transmission, Differential,
                    Suspension, Brake, Cooling, Electronics, ECU, Turbo,
                    Intercooler, Exhaust, Compatibility, Article, Shop, ShopLink, ElectricMotor, Battery, Inverter)
from functools import wraps
from datetime import datetime
from models import KnowledgeItem, Swap

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Доступ запрещён', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- ДАШБОРД ----------
@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

# ---------- BRANDS ----------
@admin_bp.route('/brands')
@admin_required
def list_brands():
    items = Brand.query.all()
    return render_template('admin/list_brands.html', items=items)

@admin_bp.route('/brands/new', methods=['GET', 'POST'])
@admin_required
def new_brand():
    if request.method == 'POST':
        item = Brand(
            name=request.form['name'],
            country=request.form.get('country', ''),
            description=request.form.get('description', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Бренд добавлен', 'success')
        return redirect(url_for('admin.list_brands'))
    return render_template('admin/edit_brand.html', item=None)

@admin_bp.route('/brands/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_brand(id):
    item = Brand.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.country = request.form.get('country', '')
        item.description = request.form.get('description', '')
        db.session.commit()
        flash('Бренд обновлён', 'success')
        return redirect(url_for('admin.list_brands'))
    return render_template('admin/edit_brand.html', item=item)

@admin_bp.route('/brands/<int:id>/delete', methods=['POST'])
@admin_required
def delete_brand(id):
    item = Brand.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Бренд удалён', 'info')
    return redirect(url_for('admin.list_brands'))

# ---------- MODELS ----------
@admin_bp.route('/models')
@admin_required
def list_models():
    items = Model.query.all()
    return render_template('admin/list_models.html', items=items)

@admin_bp.route('/models/new', methods=['GET', 'POST'])
@admin_required
def new_model():
    brands = Brand.query.all()
    if request.method == 'POST':
        item = Model(
            brand_id=request.form['brand_id'],
            name=request.form['name'],
            generation=request.form.get('generation', ''),
            year_start=request.form.get('year_start', type=int),
            year_end=request.form.get('year_end', type=int),
            body_type=request.form.get('body_type', ''),
            description=request.form.get('description', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Модель добавлена', 'success')
        return redirect(url_for('admin.list_models'))
    return render_template('admin/edit_model.html', item=None, brands=brands)

@admin_bp.route('/models/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_model(id):
    item = Model.query.get_or_404(id)
    brands = Brand.query.all()
    if request.method == 'POST':
        item.brand_id = request.form['brand_id']
        item.name = request.form['name']
        item.generation = request.form.get('generation', '')
        item.year_start = request.form.get('year_start', type=int)
        item.year_end = request.form.get('year_end', type=int)
        item.body_type = request.form.get('body_type', '')
        item.description = request.form.get('description', '')
        db.session.commit()
        flash('Модель обновлена', 'success')
        return redirect(url_for('admin.list_models'))
    return render_template('admin/edit_model.html', item=item, brands=brands)

@admin_bp.route('/models/<int:id>/delete', methods=['POST'])
@admin_required
def delete_model(id):
    item = Model.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Модель удалена', 'info')
    return redirect(url_for('admin.list_models'))

# ---------- ENGINES ----------
@admin_bp.route('/engines')
@admin_required
def list_engines():
    items = Engine.query.all()
    return render_template('admin/list_engines.html', items=items)

@admin_bp.route('/engines/new', methods=['GET', 'POST'])
@admin_required
def new_engine():
    models = Model.query.all()
    if request.method == 'POST':
        item = Engine(
            engine_code=request.form['engine_code'],
            name=request.form['name'],
            displacement=request.form.get('displacement', type=float),
            power_hp=request.form.get('power_hp', type=int),
            torque_nm=request.form.get('torque_nm', type=int),
            fuel_type=request.form.get('fuel_type', ''),
            configuration=request.form.get('configuration', ''),
            model_id=request.form.get('model_id', type=int) or None
        )
        db.session.add(item)
        db.session.commit()
        flash('Двигатель добавлен', 'success')
        return redirect(url_for('admin.list_engines'))
    return render_template('admin/edit_engine.html', item=None, models=models)

@admin_bp.route('/engines/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_engine(id):
    item = Engine.query.get_or_404(id)
    models = Model.query.all()
    if request.method == 'POST':
        item.engine_code = request.form['engine_code']
        item.name = request.form['name']
        item.displacement = request.form.get('displacement', type=float)
        item.power_hp = request.form.get('power_hp', type=int)
        item.torque_nm = request.form.get('torque_nm', type=int)
        item.fuel_type = request.form.get('fuel_type', '')
        item.configuration = request.form.get('configuration', '')
        item.model_id = request.form.get('model_id', type=int) or None
        db.session.commit()
        flash('Двигатель обновлён', 'success')
        return redirect(url_for('admin.list_engines'))
    return render_template('admin/edit_engine.html', item=item, models=models)

@admin_bp.route('/engines/<int:id>/delete', methods=['POST'])
@admin_required
def delete_engine(id):
    item = Engine.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Двигатель удалён', 'info')
    return redirect(url_for('admin.list_engines'))

# ---------- TRANSMISSIONS ----------
@admin_bp.route('/transmissions')
@admin_required
def list_transmissions():
    items = Transmission.query.all()
    return render_template('admin/list_transmissions.html', items=items)

@admin_bp.route('/transmissions/new', methods=['GET', 'POST'])
@admin_required
def new_transmission():
    if request.method == 'POST':
        item = Transmission(
            name=request.form['name'],
            type=request.form.get('type', ''),
            gears=request.form.get('gears', type=int)
        )
        db.session.add(item)
        db.session.commit()
        flash('Трансмиссия добавлена', 'success')
        return redirect(url_for('admin.list_transmissions'))
    return render_template('admin/edit_transmission.html', item=None)

@admin_bp.route('/transmissions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_transmission(id):
    item = Transmission.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.gears = request.form.get('gears', type=int)
        db.session.commit()
        flash('Трансмиссия обновлена', 'success')
        return redirect(url_for('admin.list_transmissions'))
    return render_template('admin/edit_transmission.html', item=item)

@admin_bp.route('/transmissions/<int:id>/delete', methods=['POST'])
@admin_required
def delete_transmission(id):
    item = Transmission.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Трансмиссия удалена', 'info')
    return redirect(url_for('admin.list_transmissions'))

# ---------- DIFFERENTIALS ----------
@admin_bp.route('/differentials')
@admin_required
def list_differentials():
    items = Differential.query.all()
    return render_template('admin/list_differentials.html', items=items)

@admin_bp.route('/differentials/new', methods=['GET', 'POST'])
@admin_required
def new_differential():
    if request.method == 'POST':
        item = Differential(
            name=request.form['name'],
            type=request.form.get('type', ''),
            ratio=request.form.get('ratio', type=float)
        )
        db.session.add(item)
        db.session.commit()
        flash('Редуктор добавлен', 'success')
        return redirect(url_for('admin.list_differentials'))
    return render_template('admin/edit_differential.html', item=None)

@admin_bp.route('/differentials/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_differential(id):
    item = Differential.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.ratio = request.form.get('ratio', type=float)
        db.session.commit()
        flash('Редуктор обновлён', 'success')
        return redirect(url_for('admin.list_differentials'))
    return render_template('admin/edit_differential.html', item=item)

@admin_bp.route('/differentials/<int:id>/delete', methods=['POST'])
@admin_required
def delete_differential(id):
    item = Differential.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Редуктор удалён', 'info')
    return redirect(url_for('admin.list_differentials'))

# ---------- SUSPENSIONS ----------
@admin_bp.route('/suspensions')
@admin_required
def list_suspensions():
    items = Suspension.query.all()
    return render_template('admin/list_suspensions.html', items=items)

@admin_bp.route('/suspensions/new', methods=['GET', 'POST'])
@admin_required
def new_suspension():
    if request.method == 'POST':
        item = Suspension(
            name=request.form['name'],
            type=request.form.get('type', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Подвеска добавлена', 'success')
        return redirect(url_for('admin.list_suspensions'))
    return render_template('admin/edit_suspension.html', item=None)

@admin_bp.route('/suspensions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_suspension(id):
    item = Suspension.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        db.session.commit()
        flash('Подвеска обновлена', 'success')
        return redirect(url_for('admin.list_suspensions'))
    return render_template('admin/edit_suspension.html', item=item)

@admin_bp.route('/suspensions/<int:id>/delete', methods=['POST'])
@admin_required
def delete_suspension(id):
    item = Suspension.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Подвеска удалена', 'info')
    return redirect(url_for('admin.list_suspensions'))

# ---------- BRAKES ----------
@admin_bp.route('/brakes')
@admin_required
def list_brakes():
    items = Brake.query.all()
    return render_template('admin/list_brakes.html', items=items)

@admin_bp.route('/brakes/new', methods=['GET', 'POST'])
@admin_required
def new_brake():
    if request.method == 'POST':
        item = Brake(
            name=request.form['name'],
            type=request.form.get('type', ''),
            size=request.form.get('size', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Тормоза добавлены', 'success')
        return redirect(url_for('admin.list_brakes'))
    return render_template('admin/edit_brake.html', item=None)

@admin_bp.route('/brakes/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_brake(id):
    item = Brake.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.size = request.form.get('size', '')
        db.session.commit()
        flash('Тормоза обновлены', 'success')
        return redirect(url_for('admin.list_brakes'))
    return render_template('admin/edit_brake.html', item=item)

@admin_bp.route('/brakes/<int:id>/delete', methods=['POST'])
@admin_required
def delete_brake(id):
    item = Brake.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Тормоза удалены', 'info')
    return redirect(url_for('admin.list_brakes'))

# ---------- COOLINGS ----------
@admin_bp.route('/coolings')
@admin_required
def list_coolings():
    items = Cooling.query.all()
    return render_template('admin/list_coolings.html', items=items)

@admin_bp.route('/coolings/new', methods=['GET', 'POST'])
@admin_required
def new_cooling():
    if request.method == 'POST':
        item = Cooling(
            name=request.form['name'],
            type=request.form.get('type', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Охлаждение добавлено', 'success')
        return redirect(url_for('admin.list_coolings'))
    return render_template('admin/edit_cooling.html', item=None)

@admin_bp.route('/coolings/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_cooling(id):
    item = Cooling.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        db.session.commit()
        flash('Охлаждение обновлено', 'success')
        return redirect(url_for('admin.list_coolings'))
    return render_template('admin/edit_cooling.html', item=item)

@admin_bp.route('/coolings/<int:id>/delete', methods=['POST'])
@admin_required
def delete_cooling(id):
    item = Cooling.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Охлаждение удалено', 'info')
    return redirect(url_for('admin.list_coolings'))

# ---------- ELECTRONICS ----------
@admin_bp.route('/electronics')
@admin_required
def list_electronics():
    items = Electronics.query.all()
    return render_template('admin/list_electronics.html', items=items)

@admin_bp.route('/electronics/new', methods=['GET', 'POST'])
@admin_required
def new_electronics():
    if request.method == 'POST':
        item = Electronics(
            name=request.form['name'],
            description=request.form.get('description', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Электроника добавлена', 'success')
        return redirect(url_for('admin.list_electronics'))
    return render_template('admin/edit_electronics.html', item=None)

@admin_bp.route('/electronics/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_electronics(id):
    item = Electronics.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form.get('description', '')
        db.session.commit()
        flash('Электроника обновлена', 'success')
        return redirect(url_for('admin.list_electronics'))
    return render_template('admin/edit_electronics.html', item=item)

@admin_bp.route('/electronics/<int:id>/delete', methods=['POST'])
@admin_required
def delete_electronics(id):
    item = Electronics.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Электроника удалена', 'info')
    return redirect(url_for('admin.list_electronics'))

# ---------- ECUS ----------
@admin_bp.route('/ecus')
@admin_required
def list_ecus():
    items = ECU.query.all()
    return render_template('admin/list_ecus.html', items=items)

@admin_bp.route('/ecus/new', methods=['GET', 'POST'])
@admin_required
def new_ecu():
    if request.method == 'POST':
        item = ECU(
            name=request.form['name'],
            type=request.form.get('type', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('ЭБУ добавлен', 'success')
        return redirect(url_for('admin.list_ecus'))
    return render_template('admin/edit_ecu.html', item=None)

@admin_bp.route('/ecus/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_ecu(id):
    item = ECU.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        db.session.commit()
        flash('ЭБУ обновлён', 'success')
        return redirect(url_for('admin.list_ecus'))
    return render_template('admin/edit_ecu.html', item=item)

@admin_bp.route('/ecus/<int:id>/delete', methods=['POST'])
@admin_required
def delete_ecu(id):
    item = ECU.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('ЭБУ удалён', 'info')
    return redirect(url_for('admin.list_ecus'))

# ---------- TURBOS ----------
@admin_bp.route('/turbos')
@admin_required
def list_turbos():
    items = Turbo.query.all()
    return render_template('admin/list_turbos.html', items=items)

@admin_bp.route('/turbos/new', methods=['GET', 'POST'])
@admin_required
def new_turbo():
    if request.method == 'POST':
        item = Turbo(
            name=request.form['name'],
            pressure=request.form.get('pressure', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Турбина добавлена', 'success')
        return redirect(url_for('admin.list_turbos'))
    return render_template('admin/edit_turbo.html', item=None)

@admin_bp.route('/turbos/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_turbo(id):
    item = Turbo.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.pressure = request.form.get('pressure', '')
        db.session.commit()
        flash('Турбина обновлена', 'success')
        return redirect(url_for('admin.list_turbos'))
    return render_template('admin/edit_turbo.html', item=item)

@admin_bp.route('/turbos/<int:id>/delete', methods=['POST'])
@admin_required
def delete_turbo(id):
    item = Turbo.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Турбина удалена', 'info')
    return redirect(url_for('admin.list_turbos'))

# ---------- INTERCOOLERS ----------
@admin_bp.route('/intercoolers')
@admin_required
def list_intercoolers():
    items = Intercooler.query.all()
    return render_template('admin/list_intercoolers.html', items=items)

@admin_bp.route('/intercoolers/new', methods=['GET', 'POST'])
@admin_required
def new_intercooler():
    if request.method == 'POST':
        item = Intercooler(
            name=request.form['name'],
            type=request.form.get('type', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Интеркулер добавлен', 'success')
        return redirect(url_for('admin.list_intercoolers'))
    return render_template('admin/edit_intercooler.html', item=None)

@admin_bp.route('/intercoolers/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_intercooler(id):
    item = Intercooler.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        db.session.commit()
        flash('Интеркулер обновлён', 'success')
        return redirect(url_for('admin.list_intercoolers'))
    return render_template('admin/edit_intercooler.html', item=item)

@admin_bp.route('/intercoolers/<int:id>/delete', methods=['POST'])
@admin_required
def delete_intercooler(id):
    item = Intercooler.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Интеркулер удалён', 'info')
    return redirect(url_for('admin.list_intercoolers'))

# ---------- EXHAUSTS ----------
@admin_bp.route('/exhausts')
@admin_required
def list_exhausts():
    items = Exhaust.query.all()
    return render_template('admin/list_exhausts.html', items=items)

@admin_bp.route('/exhausts/new', methods=['GET', 'POST'])
@admin_required
def new_exhaust():
    if request.method == 'POST':
        item = Exhaust(
            name=request.form['name'],
            material=request.form.get('material', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Выхлоп добавлен', 'success')
        return redirect(url_for('admin.list_exhausts'))
    return render_template('admin/edit_exhaust.html', item=None)

@admin_bp.route('/exhausts/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_exhaust(id):
    item = Exhaust.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.material = request.form.get('material', '')
        db.session.commit()
        flash('Выхлоп обновлён', 'success')
        return redirect(url_for('admin.list_exhausts'))
    return render_template('admin/edit_exhaust.html', item=item)

@admin_bp.route('/exhausts/<int:id>/delete', methods=['POST'])
@admin_required
def delete_exhaust(id):
    item = Exhaust.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Выхлоп удалён', 'info')
    return redirect(url_for('admin.list_exhausts'))

# ---------- COMPATIBILITY ----------
@admin_bp.route('/compatibilities')
@admin_required
def list_compatibilities():
    items = Compatibility.query.all()
    return render_template('admin/list_compatibilities.html', items=items)

@admin_bp.route('/compatibilities/new', methods=['GET', 'POST'])
@admin_required
def new_compatibility():
    models = Model.query.all()
    if request.method == 'POST':
        item = Compatibility(
            vehicle_model_id=request.form['vehicle_model_id'],
            component_type=request.form['component_type'],
            component_id=request.form['component_id'],
            status=request.form['status'],
            description=request.form.get('description', ''),
            estimated_cost=request.form.get('estimated_cost', type=float),
            difficulty=request.form.get('difficulty', type=int),
            notes=request.form.get('notes', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Совместимость добавлена', 'success')
        return redirect(url_for('admin.list_compatibilities'))
    return render_template('admin/edit_compatibility.html', item=None, models=models)

@admin_bp.route('/compatibilities/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_compatibility(id):
    item = Compatibility.query.get_or_404(id)
    models = Model.query.all()
    if request.method == 'POST':
        item.vehicle_model_id = request.form['vehicle_model_id']
        item.component_type = request.form['component_type']
        item.component_id = request.form['component_id']
        item.status = request.form['status']
        item.description = request.form.get('description', '')
        item.estimated_cost = request.form.get('estimated_cost', type=float)
        item.difficulty = request.form.get('difficulty', type=int)
        item.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Совместимость обновлена', 'success')
        return redirect(url_for('admin.list_compatibilities'))
    return render_template('admin/edit_compatibility.html', item=item, models=models)

@admin_bp.route('/compatibilities/<int:id>/delete', methods=['POST'])
@admin_required
def delete_compatibility(id):
    item = Compatibility.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Совместимость удалена', 'info')
    return redirect(url_for('admin.list_compatibilities'))

# ---------- ARTICLES ----------
@admin_bp.route('/articles')
@admin_required
def list_articles():
    items = Article.query.all()
    return render_template('admin/list_articles.html', items=items)

@admin_bp.route('/articles/new', methods=['GET', 'POST'])
@admin_required
def new_article():
    if request.method == 'POST':
        item = Article(
            title=request.form['title'],
            category=request.form['category'],
            content=request.form['content'],
            tags=request.form.get('tags', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Статья добавлена', 'success')
        return redirect(url_for('admin.list_articles'))
    return render_template('admin/edit_article.html', item=None)

@admin_bp.route('/articles/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_article(id):
    item = Article.query.get_or_404(id)
    if request.method == 'POST':
        item.title = request.form['title']
        item.category = request.form['category']
        item.content = request.form['content']
        item.tags = request.form.get('tags', '')
        db.session.commit()
        flash('Статья обновлена', 'success')
        return redirect(url_for('admin.list_articles'))
    return render_template('admin/edit_article.html', item=item)

@admin_bp.route('/articles/<int:id>/delete', methods=['POST'])
@admin_required
def delete_article(id):
    item = Article.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Статья удалена', 'info')
    return redirect(url_for('admin.list_articles'))

# ---------- SHOPS ----------
@admin_bp.route('/shops')
@admin_required
def list_shops():
    items = Shop.query.all()
    return render_template('admin/list_shops.html', items=items)

@admin_bp.route('/shops/new', methods=['GET', 'POST'])
@admin_required
def new_shop():
    if request.method == 'POST':
        item = Shop(
            name=request.form['name'],
            logo_url=request.form.get('logo_url', ''),
            affiliate_code=request.form.get('affiliate_code', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Магазин добавлен', 'success')
        return redirect(url_for('admin.list_shops'))
    return render_template('admin/edit_shop.html', item=None)

@admin_bp.route('/shops/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_shop(id):
    item = Shop.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.logo_url = request.form.get('logo_url', '')
        item.affiliate_code = request.form.get('affiliate_code', '')
        db.session.commit()
        flash('Магазин обновлён', 'success')
        return redirect(url_for('admin.list_shops'))
    return render_template('admin/edit_shop.html', item=item)

@admin_bp.route('/shops/<int:id>/delete', methods=['POST'])
@admin_required
def delete_shop(id):
    item = Shop.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Магазин удалён', 'info')
    return redirect(url_for('admin.list_shops'))

# ---------- SHOP LINKS ----------
@admin_bp.route('/shoplinks')
@admin_required
def list_shoplinks():
    items = ShopLink.query.all()
    return render_template('admin/list_shoplinks.html', items=items)

@admin_bp.route('/shoplinks/new', methods=['GET', 'POST'])
@admin_required
def new_shoplink():
    shops = Shop.query.all()
    compatibilities = Compatibility.query.all()
    if request.method == 'POST':
        item = ShopLink(
            compatibility_id=request.form['compatibility_id'],
            shop_id=request.form['shop_id'],
            price=request.form['price'],
            currency=request.form.get('currency', 'USD'),
            url=request.form.get('url', ''),
            in_stock=request.form.get('in_stock') == 'on'
        )
        db.session.add(item)
        db.session.commit()
        flash('Цена добавлена', 'success')
        return redirect(url_for('admin.list_shoplinks'))
    return render_template('admin/edit_shoplink.html', item=None, shops=shops, compatibilities=compatibilities)

@admin_bp.route('/shoplinks/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_shoplink(id):
    item = ShopLink.query.get_or_404(id)
    shops = Shop.query.all()
    compatibilities = Compatibility.query.all()
    if request.method == 'POST':
        item.compatibility_id = request.form['compatibility_id']
        item.shop_id = request.form['shop_id']
        item.price = request.form['price']
        item.currency = request.form.get('currency', 'USD')
        item.url = request.form.get('url', '')
        item.in_stock = request.form.get('in_stock') == 'on'
        db.session.commit()
        flash('Цена обновлена', 'success')
        return redirect(url_for('admin.list_shoplinks'))
    return render_template('admin/edit_shoplink.html', item=item, shops=shops, compatibilities=compatibilities)

@admin_bp.route('/shoplinks/<int:id>/delete', methods=['POST'])
@admin_required
def delete_shoplink(id):
    item = ShopLink.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Цена удалена', 'info')
    return redirect(url_for('admin.list_shoplinks'))

# ========== ELECTRIC MOTORS ==========
@admin_bp.route('/electric_motors')
@admin_required
def list_electric_motors():
    items = ElectricMotor.query.all()
    return render_template('admin/list_electric_motors.html', items=items)

@admin_bp.route('/electric_motors/new', methods=['GET', 'POST'])
@admin_required
def new_electric_motor():
    if request.method == 'POST':
        item = ElectricMotor(
            name=request.form['name'],
            power_hp=request.form.get('power_hp', type=int),
            torque_nm=request.form.get('torque_nm', type=int),
            motor_type=request.form.get('motor_type', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Электромотор добавлен', 'success')
        return redirect(url_for('admin.list_electric_motors'))
    return render_template('admin/edit_electric_motor.html', item=None)

@admin_bp.route('/electric_motors/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_electric_motor(id):
    item = ElectricMotor.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.power_hp = request.form.get('power_hp', type=int)
        item.torque_nm = request.form.get('torque_nm', type=int)
        item.motor_type = request.form.get('motor_type', '')
        db.session.commit()
        flash('Электромотор обновлён', 'success')
        return redirect(url_for('admin.list_electric_motors'))
    return render_template('admin/edit_electric_motor.html', item=item)

@admin_bp.route('/electric_motors/<int:id>/delete', methods=['POST'])
@admin_required
def delete_electric_motor(id):
    item = ElectricMotor.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Электромотор удалён', 'info')
    return redirect(url_for('admin.list_electric_motors'))

# ========== BATTERIES ==========
@admin_bp.route('/batteries')
@admin_required
def list_batteries():
    items = Battery.query.all()
    return render_template('admin/list_batteries.html', items=items)

@admin_bp.route('/batteries/new', methods=['GET', 'POST'])
@admin_required
def new_battery():
    if request.method == 'POST':
        item = Battery(
            name=request.form['name'],
            capacity_kwh=request.form.get('capacity_kwh', type=float),
            voltage=request.form.get('voltage', type=float),
            battery_type=request.form.get('battery_type', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Батарея добавлена', 'success')
        return redirect(url_for('admin.list_batteries'))
    return render_template('admin/edit_battery.html', item=None)

@admin_bp.route('/batteries/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_battery(id):
    item = Battery.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.capacity_kwh = request.form.get('capacity_kwh', type=float)
        item.voltage = request.form.get('voltage', type=float)
        item.battery_type = request.form.get('battery_type', '')
        db.session.commit()
        flash('Батарея обновлена', 'success')
        return redirect(url_for('admin.list_batteries'))
    return render_template('admin/edit_battery.html', item=item)

@admin_bp.route('/batteries/<int:id>/delete', methods=['POST'])
@admin_required
def delete_battery(id):
    item = Battery.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Батарея удалена', 'info')
    return redirect(url_for('admin.list_batteries'))

# ========== INVERTERS ==========
@admin_bp.route('/inverters')
@admin_required
def list_inverters():
    items = Inverter.query.all()
    return render_template('admin/list_inverters.html', items=items)

@admin_bp.route('/inverters/new', methods=['GET', 'POST'])
@admin_required
def new_inverter():
    if request.method == 'POST':
        item = Inverter(
            name=request.form['name'],
            power_kw=request.form.get('power_kw', type=float),
            inverter_type=request.form.get('inverter_type', '')
        )
        db.session.add(item)
        db.session.commit()
        flash('Инвертор добавлен', 'success')
        return redirect(url_for('admin.list_inverters'))
    return render_template('admin/edit_inverter.html', item=None)

@admin_bp.route('/inverters/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_inverter(id):
    item = Inverter.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.power_kw = request.form.get('power_kw', type=float)
        item.inverter_type = request.form.get('inverter_type', '')
        db.session.commit()
        flash('Инвертор обновлён', 'success')
        return redirect(url_for('admin.list_inverters'))
    return render_template('admin/edit_inverter.html', item=item)

@admin_bp.route('/inverters/<int:id>/delete', methods=['POST'])
@admin_required
def delete_inverter(id):
    item = Inverter.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Инвертор удалён', 'info')
    return redirect(url_for('admin.list_inverters'))

# ---------- AI KNOWLEDGE QUEUE ----------
@admin_bp.route('/knowledge-items')
@admin_required
def list_knowledge_items():
    items = KnowledgeItem.query.order_by(KnowledgeItem.created_at.desc()).all()
    return render_template('admin/list_knowledge_items.html', items=items)

@admin_bp.route('/knowledge-items/<int:id>/set-status', methods=['POST'])
@admin_required
def set_knowledge_status(id):
    item = KnowledgeItem.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['VERIFIED', 'REJECTED', 'REVIEW_REQUIRED', 'AI_GENERATED']:
        item.status = new_status
        if new_status == 'VERIFIED':
            item.verified_by = current_user.id
            item.verified_at = datetime.utcnow()
        db.session.commit()
        flash('Статус обновлён.', 'success')
    return redirect(url_for('admin.list_knowledge_items'))

@admin_bp.route('/knowledge-items/<int:id>/delete', methods=['POST'])
@admin_required
def delete_knowledge_item(id):
    item = KnowledgeItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Запись удалена.', 'info')
    return redirect(url_for('admin.list_knowledge_items'))

# ---------- SWAPS ----------
@admin_bp.route('/swaps')
@admin_required
def list_swaps():
    swaps = Swap.query.order_by(Swap.created_at.desc()).all()
    return render_template('admin/list_swaps.html', swaps=swaps)

@admin_bp.route('/swaps/<int:id>/set-status', methods=['POST'])
@admin_required
def set_swap_status(id):
    swap = Swap.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['VERIFIED', 'REJECTED', 'REVIEW_REQUIRED', 'AI_GENERATED']:
        swap.status = new_status
        if new_status == 'VERIFIED':
            swap.verified_by = current_user.id
            swap.verified_at = datetime.utcnow()
        db.session.commit()
        flash('Статус свапа обновлён.', 'success')
    return redirect(url_for('admin.list_swaps'))

@admin_bp.route('/swaps/<int:id>/delete', methods=['POST'])
@admin_required
def delete_swap(id):
    swap = Swap.query.get_or_404(id)
    db.session.delete(swap)
    db.session.commit()
    flash('Свап удалён.', 'info')
    return redirect(url_for('admin.list_swaps'))
