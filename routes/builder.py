from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user, login_required
from services.builder import (
    init_builder, set_vehicle, get_vehicle,
    get_compatible_components, set_component, get_component,
    get_summary, save_project, get_shop_prices
)
from services.catalog import get_all_brands, get_models_by_brand, get_brand_by_id
from models import Swap

builder_bp = Blueprint('builder', __name__, url_prefix='/builder')

BUILDER_STEPS = ['vehicle', 'engine', 'transmission', 'differential',
                 'suspension', 'brakes', 'cooling', 'electronics', 'ecu', 'turbo',
                 'intercooler', 'exhaust']

@builder_bp.before_request
def ensure_builder_session():
    init_builder()

@builder_bp.route('/')
def index():
    vehicle = get_vehicle()
    if not vehicle:
        return redirect(url_for('builder.select_vehicle'))
    selections = {
        'engine': get_component('engine'),
        'transmission': get_component('transmission'),
        'differential': get_component('differential'),
        'suspension': get_component('suspension'),
        'brakes': get_component('brakes'),
        'cooling': get_component('cooling'),
        'electronics': get_component('electronics'),
        'ecu': get_component('ecu'),
        'turbo': get_component('turbo'),
        'intercooler': get_component('intercooler'),
        'exhaust': get_component('exhaust'),
        'exhaust': get_component('exhaust'),
        'electric_motor': get_component('electric_motor'),
        'battery': get_component('battery'),
        'inverter': get_component('inverter'),
}
    summary = get_summary()
    return render_template('builder/index.html',
                           vehicle=vehicle,
                           selections=selections,
                           summary=summary,
                           steps=BUILDER_STEPS)

@builder_bp.route('/select-vehicle')
def select_vehicle():
    brands = get_all_brands()
    brand_id = request.args.get('brand_id', type=int)
    models = None
    selected_brand = None
    if brand_id:
        selected_brand = get_brand_by_id(brand_id)
        models = get_models_by_brand(brand_id)
    return render_template('builder/select_vehicle.html',
                           brands=brands,
                           models=models,
                           selected_brand=selected_brand)

@builder_bp.route('/set-vehicle/<int:model_id>')
def set_vehicle_route(model_id):
    model = set_vehicle(model_id)
    if not model:
        return "Модель не найдена", 404
    return redirect(url_for('builder.index'))

@builder_bp.route('/select-component/<component_type>')
def select_component(component_type):
    vehicle = get_vehicle()
    if not vehicle:
        return redirect(url_for('builder.select_vehicle'))
    items = get_compatible_components(vehicle['id'], component_type)
    # Добавляем цены для каждого элемента
    for item in items:
        item['prices'] = get_shop_prices(item['compatibility_id']) if item['compatibility_id'] else []
    component_names = {
    'engine': 'двигатель',
    'transmission': 'КПП',
    'differential': 'редуктор',
    'suspension': 'подвеска',
    'brakes': 'тормоза',
    'cooling': 'охлаждение',
    'electronics': 'электроника',
    'ecu': 'ЭБУ',
    'turbo': 'турбина',
    'intercooler': 'интеркулер',
    'exhaust': 'выхлоп',
    'electric_motor': 'электромотор',
    'battery': 'батарея',
    'inverter': 'инвертор'
}
    return render_template('builder/select_component.html',
                           vehicle=vehicle,
                           component_type=component_type,
                           component_label=component_names.get(component_type, component_type),
                           items=items)

@builder_bp.route('/set-component/<component_type>/<int:item_id>')
def set_component_route(component_type, item_id):
    if not set_component(component_type, item_id):
        return "Компонент не найден", 404
    return redirect(url_for('builder.index'))

@builder_bp.route('/save', methods=['POST'])
@login_required
def save():
    name = request.form.get('project_name', 'Без названия')
    is_public = request.form.get('is_public') == 'on'
    project = save_project(name, current_user.id, is_public)
    if project:
        flash(f'Проект "{name}" сохранён!', 'success')
    else:
        flash('Ошибка при сохранении. Проверьте, что выбран автомобиль.', 'danger')
    return redirect(url_for('builder.index'))
# API для 3D-схемы: возвращает список компонентов в JSON
@builder_bp.route('/api/components/<int:vehicle_model_id>/<component_type>')
def api_components(vehicle_model_id, component_type):
    items = get_compatible_components(vehicle_model_id, component_type)
    # Преобразуем объекты в словари
    result = []
    for item in items:
        result.append({
            'id': item['item'].id,
            'name': item['item'].name,
            'status': item['status'],
            'description': item['description'],
            'estimated_cost': item['estimated_cost'],
            'difficulty': item['difficulty']
        })

@builder_bp.route('/swaps/<component_type>/<int:component_id>')
def view_swaps(component_type, component_id):
    vehicle = get_vehicle()
    if not vehicle:
        return redirect(url_for('builder.select_vehicle'))

       # Для примера используем выбранный автомобиль (vehicle['id'])
    vehicle_model_id = vehicle['id']

    # Получаем список свапов для данного исходного компонента
    swaps = Swap.query.filter_by(
        source_vehicle_model_id=vehicle_model_id,
        source_component_type=component_type,
        source_component_id=component_id
    ).all()

    # Если свапов нет, можно показать заглушку или сгенерировать один?
    # Пока просто передадим в шаблон
    return render_template('builder/swaps.html', swaps=swaps, component_type=component_type, component_id=component_id, vehicle=vehicle)

@builder_bp.route('/generate-swap/<component_type>/<int:component_id>', methods=['GET', 'POST'])
def generate_swap(component_type, component_id):
    vehicle = get_vehicle()
    if not vehicle:
        return redirect(url_for('builder.select_vehicle'))
    vehicle_model_id = vehicle['id']

    # Для простоты поддерживаем только двигатели
    if component_type != 'engine':
        flash('Пока генерация свапов доступна только для двигателей.', 'info')
        return redirect(url_for('builder.view_swaps', component_type=component_type, component_id=component_id))

    if request.method == 'POST':
        target_component_id = request.form.get('target_component_id', type=int)
        if not target_component_id:
            flash('Выберите целевой двигатель.', 'danger')
            return redirect(url_for('builder.generate_swap', component_type=component_type, component_id=component_id))

        from services.compatibility_engine import generate_swap_and_save
        swap = generate_swap_and_save(
            source_vehicle_model_id=vehicle_model_id,
            source_component_type=component_type,
            source_component_id=component_id,
            target_component_type=component_type,
            target_component_id=target_component_id
        )
        flash('Свап сгенерирован и сохранён!', 'success')
        return redirect(url_for('builder.view_swaps', component_type=component_type, component_id=component_id))

    # GET-запрос: отобразить форму выбора
    from models import Engine
    engines = Engine.query.all()
    return render_template('builder/generate_swap.html', engines=engines, component_type=component_type, component_id=component_id, vehicle=vehicle)

    return {'components': result}
