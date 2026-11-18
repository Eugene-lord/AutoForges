from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user, login_required
from services.builder import (
    init_builder, set_vehicle, get_vehicle,
    get_compatible_components, set_component, get_component,
    get_summary, save_project, get_shop_prices
)
from services.catalog import get_all_brands, get_models_by_brand, get_brand_by_id
from models import Swap
from extensions import limiter
from datetime import datetime, timezone
from extensions import csrf
from flask import jsonify, current_app
from models import Brand, Model, Generation, GenerationJob
from services.generation_service import COMPONENT_MODELS
from services.job_runner import enqueue_job

builder_bp = Blueprint('builder', __name__, url_prefix='/builder')

BUILDER_STEPS = ['vehicle', 'engine', 'transmission', 'differential',
                 'suspension', 'brakes', 'cooling', 'electronics', 'ecu', 'turbo',
                 'intercooler', 'exhaust']

@builder_bp.before_request
def ensure_builder_session():
    init_builder()

# Координаты узлов на схеме (центры зон) — должны совпадать с SVG
PART_POSITIONS = {
    'engine':        {'x': 240, 'y': 200},
    'transmission':  {'x': 347, 'y': 200},
    'differential':  {'x': 590, 'y': 200},
    'cooling':       {'x': 127, 'y': 200},
    'intercooler':   {'x': 90,  'y': 200},
    'turbo':         {'x': 220, 'y': 150},
    'ecu':           {'x': 407, 'y': 142},
    'electronics':   {'x': 685, 'y': 165},
    'exhaust':       {'x': 500, 'y': 250},
    'susp_fl':       {'x': 170, 'y': 105},
    'susp_fr':       {'x': 170, 'y': 295},
    'susp_rl':       {'x': 620, 'y': 105},
    'susp_rr':       {'x': 620, 'y': 295},
}


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
    }

    # Автоматические связи по правилам
    CONNECTION_RULES = [
        ('engine', 'transmission', 'mechanical', 'Сцепление'),
        ('transmission', 'differential', 'mechanical', 'Кардан'),
        ('differential', 'suspension', 'mechanical', 'Полуось'),
        ('ecu', 'engine', 'control', 'Управление двигателем'),
        ('cooling', 'engine', 'cooling', 'Контур охлаждения'),
        ('turbo', 'engine', 'air', 'Наддув'),
        ('intercooler', 'turbo', 'air', 'Интеркулер → турбина'),
        ('engine', 'exhaust', 'exhaust', 'Выпуск'),
        ('electronics', 'ecu', 'electrical', 'Проводка ЭБУ'),
    ]

    connections = []
    for src_type, tgt_type, conn_type, label in CONNECTION_RULES:
        src_selected = selections.get(src_type) is not None
        tgt_selected = selections.get(tgt_type) is not None
        
        # Для полуоси: если выбран редуктор, подвеска считается "выбранной"
        if src_type == 'differential' and tgt_type == 'suspension':
            tgt_selected = selections.get('differential') is not None
        
        if not (src_selected and tgt_selected):
            continue
        
        src_pos = PART_POSITIONS.get(src_type)
        tgt_pos = PART_POSITIONS.get(tgt_type)
        if not src_pos or not tgt_pos:
            continue
        
        connections.append({
            'x1': src_pos['x'], 'y1': src_pos['y'],
            'x2': tgt_pos['x'], 'y2': tgt_pos['y'],
            'type': conn_type,
            'label': label,
            'from': src_type,
            'to': tgt_type,
        })

    summary = get_summary()

    return render_template('builder/index.html',
                           vehicle=vehicle,
                           selections=selections,
                           summary=summary,
                           steps=BUILDER_STEPS,
                           connections=connections)

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

@builder_bp.route('/select-brand', methods=['GET', 'POST'])
def select_brand():
    from models import Brand, KnowledgeItem, db
    from services.knowledge_service import generate_brand_models
    from datetime import datetime
    import json

    generated_models = None
    new_brand_name = None

    if request.method == 'POST':
        brand_name = request.form.get('brand_name', '').strip()
        if brand_name:
            existing_brand = Brand.query.filter_by(name=brand_name).first()
            if existing_brand:
                return redirect(url_for('builder.select_vehicle', brand_id=existing_brand.id))
            else:
                try:
                    data = generate_brand_models(brand_name)
                    models = data.get('models', [])
                    item = KnowledgeItem(
                        knowledge_type='brand_models',
                        source='ai',
                        confidence=0.6,
                        risk_level='LOW',
                        status='AI_GENERATED',
                        data_json=json.dumps({'brand': brand_name, 'models': models}, ensure_ascii=False),
                        created_at=datetime.now(timezone.utc)(),
                        updated_at=datetime.now(timezone.utc)()
                    )
                    db.session.add(item)
                    db.session.commit()
                    generated_models = models
                    new_brand_name = brand_name
                except Exception as e:
                    db.session.rollback()
                    print("ERROR in select_brand:", e)  # ← вывод в терминал
                    flash(f'Ошибка: {e}', 'danger')
        else:
            flash('Введите название бренда.', 'warning')

    brands = Brand.query.order_by(Brand.name).all()
    return render_template('builder/select_brand.html',
                           brands=brands,
                           generated_models=generated_models,
                           new_brand_name=new_brand_name)

@builder_bp.route('/set-vehicle/<int:model_id>')
def set_vehicle_route(model_id):
    model = set_vehicle(model_id)
    if not model:
        return "Модель не найдена", 404
    return redirect(url_for('builder.index'))

@builder_bp.route('/select-component/<component_type>')
def select_component(component_type):
    from models import Swap, Engine
    import json

    vehicle = get_vehicle()
    if not vehicle:
        return redirect(url_for('builder.select_vehicle'))
    items = get_compatible_components(vehicle['id'], component_type)
    # Добавляем цены для каждого элемента
    for item in items:
        item['prices'] = get_shop_prices(item['compatibility_id']) if item['compatibility_id'] else []

    # Если выбираем двигатель — подтягиваем свапы для каждого
    if component_type == 'engine':
        for item in items:
            engine_id = item['item'].id
            raw_swaps = Swap.query.filter_by(
                source_vehicle_model_id=vehicle['id'],
                source_component_type='engine',
                source_component_id=engine_id
            ).all()
            swaps_data = []
            for s in raw_swaps:
                tgt = Engine.query.get(s.target_component_id)
                swaps_data.append({
                    'swap': s,
                    'target_engine': tgt.name if tgt else '?',
                    'target_hp': tgt.power_hp if tgt else '?',
                    'modifications': json.loads(s.required_modifications) if s.required_modifications else [],
                    'parts': json.loads(s.required_parts) if s.required_parts else [],
                })
            item['swaps'] = swaps_data

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
@limiter.limit("10 per hour")
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

@builder_bp.route('/api/brands')
def api_brands():
    """Список брендов. Если пусто — создать Job generate_brands."""
    brands = Brand.query.order_by(Brand.name).all()
    if not brands:
        job_id = enqueue_job(current_app._get_current_object(), 'generate_brands', {})
        return jsonify({
            'brands': [],
            'job_id': job_id,
            'status': 'pending',
            'message': 'AI не подключён. Задача создана, но данные не сгенерированы.'
        })
    return jsonify({
        'brands': [{'id': b.id, 'name': b.name, 'country': b.country} for b in brands],
        'job_id': None,
        'status': 'ok'
    })


@builder_bp.route('/api/models/<int:brand_id>')
def api_models(brand_id):
    """Список моделей бренда. Если пусто — создать Job generate_models."""
    brand = Brand.query.get_or_404(brand_id)
    models = Model.query.filter_by(brand_id=brand_id).order_by(Model.name).all()
    if not models:
        job_id = enqueue_job(current_app._get_current_object(),
                             'generate_models', {'brand_id': brand_id})
        return jsonify({
            'brand': {'id': brand.id, 'name': brand.name},
            'models': [],
            'job_id': job_id,
            'status': 'pending'
        })
    return jsonify({
        'brand': {'id': brand.id, 'name': brand.name},
        'models': [{'id': m.id, 'name': m.name, 'generation': m.generation,
                    'year_start': m.year_start, 'year_end': m.year_end} for m in models],
        'job_id': None,
        'status': 'ok'
    })


@builder_bp.route('/api/generations/<int:model_id>')
def api_generations(model_id):
    """Список поколений модели."""
    model = Model.query.get_or_404(model_id)
    gens = Generation.query.filter_by(model_id=model_id).order_by(Generation.name).all()
    if not gens:
        job_id = enqueue_job(current_app._get_current_object(),
                             'generate_generations', {'model_id': model_id})
        return jsonify({
            'model': {'id': model.id, 'name': model.name},
            'generations': [],
            'job_id': job_id,
            'status': 'pending'
        })
    return jsonify({
        'model': {'id': model.id, 'name': model.name},
        'generations': [{'id': g.id, 'name': g.name,
                         'year_start': g.year_start, 'year_end': g.year_end,
                         'body_types': g.body_types, 'markets': g.markets} for g in gens],
        'job_id': None,
        'status': 'ok'
    })


@builder_bp.route('/api/components_v2/<int:model_id>/<component_type>')
def api_components_v2(model_id, component_type):
    """Список компонентов типа для модели (через Compatibility)."""
    from models import Compatibility
    model = Model.query.get_or_404(model_id)
    model_class = COMPONENT_MODELS.get(component_type)
    if not model_class:
        return jsonify({'error': 'unknown component_type'}), 404

    comps = Compatibility.query.filter_by(
        vehicle_model_id=model_id, component_type=component_type
    ).all()

    items = []
    for c in comps:
        obj = model_class.query.get(c.component_id)
        if not obj:
            continue
        items.append({
            'id': obj.id,
            'name': obj.name,
            'status': c.status,
            'description': c.description,
            'estimated_cost': c.estimated_cost,
            'difficulty': c.difficulty,
        })

    if not items:
        job_id = enqueue_job(current_app._get_current_object(),
                             'generate_components',
                             {'model_id': model_id, 'component_type': component_type})
        return jsonify({
            'model': {'id': model.id, 'name': model.name},
            'component_type': component_type,
            'components': [],
            'job_id': job_id,
            'status': 'pending'
        })

    return jsonify({
        'model': {'id': model.id, 'name': model.name},
        'component_type': component_type,
        'components': items,
        'job_id': None,
        'status': 'ok'
    })


@builder_bp.route('/api/job/<int:job_id>')
def api_job_status(job_id):
    """Статус задачи генерации."""
    job = GenerationJob.query.get_or_404(job_id)
    return jsonify({
        'id': job.id,
        'job_type': job.job_type,
        'status': job.status,
        'result': job.result_json,
        'error': job.error,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'finished_at': job.finished_at.isoformat() if job.finished_at else None,
    })