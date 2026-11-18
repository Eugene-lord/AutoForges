from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import (db, Brand, Model, Engine, Transmission, Differential,
                    Suspension, Brake, Cooling, Electronics, ECU, Turbo,
                    Intercooler, Exhaust, Compatibility, Article, Shop, ShopLink, ElectricMotor, Battery, Inverter, Connection)
from functools import wraps
from datetime import datetime, timezone
from models import KnowledgeItem, Swap
import json

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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Engine(
            engine_code=request.form['engine_code'],
            name=request.form['name'],
            displacement=request.form.get('displacement', type=float),
            power_hp=request.form.get('power_hp', type=int),
            torque_nm=request.form.get('torque_nm', type=int),
            fuel_type=request.form.get('fuel_type', ''),
            configuration=request.form.get('configuration', ''),
            model_id=request.form.get('model_id', type=int) or None,
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.engine_code = request.form['engine_code']
        item.name = request.form['name']
        item.displacement = request.form.get('displacement', type=float)
        item.power_hp = request.form.get('power_hp', type=int)
        item.torque_nm = request.form.get('torque_nm', type=int)
        item.fuel_type = request.form.get('fuel_type', '')
        item.configuration = request.form.get('configuration', '')
        item.model_id = request.form.get('model_id', type=int) or None
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Transmission(
            name=request.form['name'],
            type=request.form.get('type', ''),
            gears=request.form.get('gears', type=int),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.gears = request.form.get('gears', type=int)
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Differential(
            name=request.form['name'],
            type=request.form.get('type', ''),
            ratio=request.form.get('ratio', type=float),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.ratio = request.form.get('ratio', type=float)
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Suspension(
            name=request.form['name'],
            type=request.form.get('type', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Brake(
            name=request.form['name'],
            type=request.form.get('type', ''),
            size=request.form.get('size', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.size = request.form.get('size', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Cooling(
            name=request.form['name'],
            type=request.form.get('type', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Electronics(
            name=request.form['name'],
            description=request.form.get('description', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.description = request.form.get('description', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = ECU(
            name=request.form['name'],
            type=request.form.get('type', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Turbo(
            name=request.form['name'],
            pressure=request.form.get('pressure', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.pressure = request.form.get('pressure', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Intercooler(
            name=request.form['name'],
            type=request.form.get('type', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.type = request.form.get('type', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item = Exhaust(
            name=request.form['name'],
            material=request.form.get('material', ''),
            source=source,
            verified_by=current_user.id if is_verified else None,
            verified_at=datetime.now(timezone.utc)() if is_verified else None
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
        source = request.form.get('source', 'manual')
        is_verified = request.form.get('is_verified') == 'on'
        item.name = request.form['name']
        item.material = request.form.get('material', '')
        item.source = source
        if is_verified:
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
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
            item.verified_at = datetime.now(timezone.utc)()
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
    from services.builder import COMPONENT_MODELS
    swaps = Swap.query.order_by(Swap.created_at.desc()).all()

    # Собираем названия компонентов
    enriched = []
    for s in swaps:
        src_model = COMPONENT_MODELS.get(s.source_component_type)
        tgt_model = COMPONENT_MODELS.get(s.target_component_type)
        src_name = '?'
        tgt_name = '?'
        if src_model:
            obj = src_model.query.get(s.source_component_id)
            if obj:
                src_name = obj.name
        if tgt_model:
            obj = tgt_model.query.get(s.target_component_id)
            if obj:
                tgt_name = obj.name
        enriched.append({'swap': s, 'src_name': src_name, 'tgt_name': tgt_name})

    return render_template('admin/list_swaps.html', swaps=swaps, enriched=enriched)

@admin_bp.route('/swaps/<int:id>/set-status', methods=['POST'])
@admin_required
def set_swap_status(id):
    swap = Swap.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['VERIFIED', 'REJECTED', 'REVIEW_REQUIRED', 'AI_GENERATED']:
        swap.status = new_status
        if new_status == 'VERIFIED':
            swap.verified_by = current_user.id
            swap.verified_at = datetime.now(timezone.utc)()
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

# ---------- CONNECTIONS ----------
@admin_bp.route('/connections')
@admin_required
def list_connections():
    from models import Connection, Model, Brand
    items = Connection.query.order_by(Connection.vehicle_model_id, Connection.connection_type).all()
    # Обогащаем названиями моделей
    enriched = []
    for c in items:
        m = Model.query.get(c.vehicle_model_id)
        b = Brand.query.get(m.brand_id) if m else None
        enriched.append({
            'conn': c,
            'vehicle_name': f"{b.name} {m.name} {m.generation}" if (b and m) else f"model_id={c.vehicle_model_id}"
        })
    return render_template('admin/list_connections.html', enriched=enriched)


@admin_bp.route('/connections/new', methods=['GET', 'POST'])
@admin_required
def new_connection():
    from models import Connection, Model
    models_list = Model.query.order_by(Model.name).all()

    if request.method == 'POST':
        item = Connection(
            vehicle_model_id=request.form.get('vehicle_model_id', type=int),
            source_part_id=request.form.get('source_part_id', '').strip(),
            target_part_id=request.form.get('target_part_id', '').strip(),
            connection_type=request.form.get('connection_type', 'mechanical'),
            label=request.form.get('label', ''),
            description=request.form.get('description', ''),
            pinout_json=request.form.get('pinout_json', ''),
            notes=request.form.get('notes', ''),
            source='manual',
            verified_by=current_user.id,
            verified_at=datetime.now(timezone.utc)(),
            created_at=datetime.now(timezone.utc)(),
            updated_at=datetime.now(timezone.utc)()
        )
        db.session.add(item)
        db.session.commit()
        flash('Связь добавлена', 'success')
        return redirect(url_for('admin.list_connections'))

    return render_template('admin/edit_connection.html', item=None, models_list=models_list)


@admin_bp.route('/connections/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_connection(id):
    from models import Connection, Model
    item = Connection.query.get_or_404(id)
    models_list = Model.query.order_by(Model.name).all()

    if request.method == 'POST':
        item.vehicle_model_id = request.form.get('vehicle_model_id', type=int)
        item.source_part_id = request.form.get('source_part_id', '').strip()
        item.target_part_id = request.form.get('target_part_id', '').strip()
        item.connection_type = request.form.get('connection_type', 'mechanical')
        item.label = request.form.get('label', '')
        item.description = request.form.get('description', '')
        item.pinout_json = request.form.get('pinout_json', '')
        item.notes = request.form.get('notes', '')
        item.updated_at = datetime.now(timezone.utc)()
        db.session.commit()
        flash('Связь обновлена', 'success')
        return redirect(url_for('admin.list_connections'))

    return render_template('admin/edit_connection.html', item=item, models_list=models_list)


@admin_bp.route('/connections/<int:id>/delete', methods=['POST'])
@admin_required
def delete_connection(id):
    from models import Connection
    item = Connection.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Связь удалена', 'info')
    return redirect(url_for('admin.list_connections'))

@admin_bp.route('/swaps/new', methods=['GET', 'POST'])
@admin_required
def new_swap():
    from services.builder import COMPONENT_MODELS
    import json

    component_types = list(COMPONENT_MODELS.keys())

    if request.method == 'POST':
        comp_type = request.form.get('component_type', 'engine')
        source_id = request.form.get('source_component_id', type=int)
        target_id = request.form.get('target_component_id', type=int)

        if not source_id or not target_id:
            flash('Выберите исходный и целевой компонент', 'danger')
            return redirect(url_for('admin.new_swap'))

        if source_id == target_id:
            flash('Исходный и целевой компонент не могут совпадать', 'warning')
            return redirect(url_for('admin.new_swap'))

        mods_text = request.form.get('required_modifications', '')
        parts_text = request.form.get('required_parts', '')
        mods_list = [m.strip() for m in mods_text.split('\n') if m.strip()]
        parts_list = [p.strip() for p in parts_text.split('\n') if p.strip()]

        item = Swap(
            source_vehicle_model_id=request.form.get('source_vehicle_model_id', type=int),
            source_component_type=comp_type,
            source_component_id=source_id,
            target_component_type=comp_type,
            target_component_id=target_id,
            transmission_id=None,
            difficulty=request.form.get('difficulty', type=int) or 1,
            required_modifications=json.dumps(mods_list, ensure_ascii=False),
            required_parts=json.dumps(parts_list, ensure_ascii=False),
            notes=request.form.get('notes', ''),
            status=request.form.get('status', 'REVIEW_REQUIRED'),
            source='manual',
            confidence=0.8,
            risk_level=request.form.get('risk_level', 'MEDIUM'),
            verified_by=current_user.id if request.form.get('status') == 'VERIFIED' else None,
            verified_at=datetime.now(timezone.utc)() if request.form.get('status') == 'VERIFIED' else None,
            created_at=datetime.now(timezone.utc)(),
            updated_at=datetime.now(timezone.utc)()
        )
        db.session.add(item)
        db.session.commit()
        flash('Свап добавлен', 'success')
        return redirect(url_for('admin.list_swaps'))

    models_list = Model.query.order_by(Model.name).all()
    return render_template('admin/edit_swap.html',
                           item=None,
                           models_list=models_list,
                           component_types=component_types,
                           pre_source_items=[],
                           pre_target_items=[],
                           mods_str='',
                           parts_str='')


@admin_bp.route('/swaps/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_swap(id):
    from services.builder import COMPONENT_MODELS
    import json

    item = Swap.query.get_or_404(id)
    component_types = list(COMPONENT_MODELS.keys())
    models_list = Model.query.order_by(Model.name).all()

    if request.method == 'POST':
        comp_type = request.form.get('component_type', item.source_component_type)
        source_id = request.form.get('source_component_id', type=int)
        target_id = request.form.get('target_component_id', type=int)

        if not source_id or not target_id:
            flash('Выберите исходный и целевой компонент', 'danger')
            return redirect(url_for('admin.edit_swap', id=id))

        mods_text = request.form.get('required_modifications', '')
        parts_text = request.form.get('required_parts', '')
        item.source_vehicle_model_id = request.form.get('source_vehicle_model_id', type=int)
        item.source_component_type = comp_type
        item.source_component_id = source_id
        item.target_component_type = comp_type
        item.target_component_id = target_id
        item.difficulty = request.form.get('difficulty', type=int) or 1
        item.required_modifications = json.dumps(
            [m.strip() for m in mods_text.split('\n') if m.strip()], ensure_ascii=False)
        item.required_parts = json.dumps(
            [p.strip() for p in parts_text.split('\n') if p.strip()], ensure_ascii=False)
        item.notes = request.form.get('notes', '')
        item.status = request.form.get('status', 'REVIEW_REQUIRED')
        item.risk_level = request.form.get('risk_level', 'MEDIUM')
        if item.status == 'VERIFIED':
            item.verified_by = current_user.id
            item.verified_at = datetime.now(timezone.utc)()
        else:
            item.verified_by = None
            item.verified_at = None
        item.updated_at = datetime.now(timezone.utc)()
        db.session.commit()
        flash('Свап обновлён', 'success')
        return redirect(url_for('admin.list_swaps'))

    # Подготовка данных для формы (JSON → строки, списки компонентов)
    mods_str = ''
    parts_str = ''
    if item.required_modifications:
        try:
            mods_str = '\n'.join(json.loads(item.required_modifications))
        except Exception:
            pass
    if item.required_parts:
        try:
            parts_str = '\n'.join(json.loads(item.required_parts))
        except Exception:
            pass

    # Списки компонентов для текущего типа
    model_class = COMPONENT_MODELS.get(item.source_component_type)
    pre_items = []
    if model_class:
        for c in model_class.query.order_by(model_class.id).all():
            label = c.name
            if item.source_component_type == 'engine':
                label += f" ({c.power_hp} л.с.)" if c.power_hp else ''
            elif item.source_component_type == 'transmission':
                label += f" ({c.type}, {c.gears}ст)" if c.type else ''
            elif item.source_component_type == 'differential':
                label += f" (ratio={c.ratio})" if c.ratio else ''
            elif item.source_component_type == 'brakes':
                label += f" ({c.size})" if c.size else ''
            elif item.source_component_type == 'turbo':
                label += f" ({c.pressure})" if c.pressure else ''
            pre_items.append({'id': c.id, 'label': label})

    return render_template('admin/edit_swap.html',
                           item=item,
                           models_list=models_list,
                           component_types=component_types,
                           pre_source_items=pre_items,
                           pre_target_items=pre_items,
                           mods_str=mods_str,
                           parts_str=parts_str)

@admin_bp.route('/api/components/<component_type>')
@admin_required
def api_components_by_type(component_type):
    """Возвращает JSON-список компонентов указанного типа для формы свапа."""
    from services.builder import COMPONENT_MODELS
    from flask import jsonify

    model_class = COMPONENT_MODELS.get(component_type)
    if not model_class:
        return jsonify({'error': 'unknown type'}), 404

    items = model_class.query.order_by(model_class.id).all()
    result = []
    for item in items:
        # Универсальное описание — берём name + специфичное поле
        label = item.name
        if component_type == 'engine':
            label += f" ({item.power_hp} л.с.)" if item.power_hp else ''
        elif component_type == 'transmission':
            label += f" ({item.type}, {item.gears}ст)" if item.type else ''
        elif component_type == 'differential':
            label += f" (ratio={item.ratio})" if item.ratio else ''
        elif component_type == 'brakes':
            label += f" ({item.size})" if item.size else ''
        elif component_type == 'turbo':
            label += f" ({item.pressure})" if item.pressure else ''
        result.append({'id': item.id, 'label': label})

    return jsonify(result)

@admin_bp.route('/knowledge-items/<int:id>/approve', methods=['POST'])
@admin_required
def approve_knowledge_item(id):
    item = KnowledgeItem.query.get_or_404(id)
    if item.knowledge_type != 'brand_models':
        flash('Одобрение поддерживается только для типа brand_models', 'warning')
        return redirect(url_for('admin.list_knowledge_items'))

    data = json.loads(item.data_json)
    brand_name = data.get('brand')
    models = data.get('models', [])

    if not brand_name:
        flash('В данных нет названия бренда', 'danger')
        return redirect(url_for('admin.list_knowledge_items'))

    # Создаём бренд, если его ещё нет
    brand = Brand.query.filter_by(name=brand_name).first()
    if not brand:
        brand = Brand(name=brand_name)
        db.session.add(brand)
        db.session.flush()

    # Создаём модели
    for model_name in models:
        existing_model = Model.query.filter_by(brand_id=brand.id, name=model_name).first()
        if not existing_model:
            db.session.add(Model(brand_id=brand.id, name=model_name, generation=''))

    item.status = 'VERIFIED'
    item.verified_by = current_user.id
    item.verified_at = datetime.now(timezone.utc)()
    db.session.commit()
    flash('Бренд и модели созданы, знание подтверждено.', 'success')
    return redirect(url_for('admin.list_knowledge_items'))

# ---------- AI INFRASTRUCTURE MONITORING ----------
@admin_bp.route('/coverage')
@admin_required
def coverage_dashboard():
    from models import CatalogCoverage, Brand, Model
    from services.generation_service import calculate_model_coverage

    # Все бренды + их модели
    brands = Brand.query.order_by(Brand.name).all()
    rows = []
    for b in brands:
        models = Model.query.filter_by(brand_id=b.id).all()
        for m in models:
            cov = calculate_model_coverage(m.id)
            rows.append({
                'brand': b.name,
                'model': f"{m.name} {m.generation or ''}".strip(),
                'model_id': m.id,
                'level': cov['level'],
                'details': cov['details'],
            })

    return render_template('admin/coverage.html', rows=rows)


@admin_bp.route('/jobs')
@admin_required
def jobs_list():
    from models import GenerationJob
    jobs = GenerationJob.query.order_by(GenerationJob.created_at.desc()).limit(100).all()
    return render_template('admin/jobs.html', jobs=jobs)


@admin_bp.route('/jobs/new', methods=['POST'])
@admin_required
def jobs_new():
    from flask import current_app
    from services.job_runner import enqueue_job
    job_type = request.form.get('job_type', '').strip()
    params_json = request.form.get('params_json', '').strip()

    params = None
    if params_json:
        try:
            import json as _json
            params = _json.loads(params_json)
        except Exception as e:
            flash(f'Ошибка в JSON params: {e}', 'danger')
            return redirect(url_for('admin.jobs_list'))

    if not job_type:
        flash('Укажите job_type', 'danger')
        return redirect(url_for('admin.jobs_list'))

    job_id = enqueue_job(current_app._get_current_object(), job_type, params)
    flash(f'Задача #{job_id} создана', 'success')
    return redirect(url_for('admin.jobs_list'))


@admin_bp.route('/jobs/<int:id>')
@admin_required
def job_detail(id):
    from models import GenerationJob
    job = GenerationJob.query.get_or_404(id)
    return render_template('admin/job_detail.html', job=job)


@admin_bp.route('/sources')
@admin_required
def sources_list():
    from models import Source
    sources = Source.query.order_by(Source.created_at.desc()).all()
    return render_template('admin/sources.html', sources=sources)


@admin_bp.route('/sources/new', methods=['POST'])
@admin_required
def sources_new():
    from models import Source
    src = Source(
        source_type=request.form.get('source_type', 'real_project'),
        url=request.form.get('url', ''),
        title=request.form.get('title', ''),
        description=request.form.get('description', ''),
        reliability=request.form.get('reliability', 'medium'),
    )
    db.session.add(src)
    db.session.commit()
    flash('Источник добавлен', 'success')
    return redirect(url_for('admin.sources_list'))