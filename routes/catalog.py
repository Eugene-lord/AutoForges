from flask import Blueprint, render_template
from services.catalog import get_all_brands, get_brand_by_id, get_models_by_brand, get_model_detail
from flask import Blueprint, render_template, request, url_for, redirect, flash
from models import Brand
catalog_bp = Blueprint('catalog', __name__)
import json

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
    from models import (Compatibility, Engine, Transmission, Differential,
                        Suspension, Brake, Cooling, Electronics, ECU, Turbo,
                        Intercooler, Exhaust, Swap)
    import json

    model, _ = get_model_detail(model_id)

        # Собираем все совместимости для этой модели
    comps = Compatibility.query.filter_by(vehicle_model_id=model_id).all()

    # Дедупликация по (component_type, component_id) — оставляем запись с наибольшим id
    seen = {}
    for c in comps:
        key = (c.component_type, c.component_id)
        if key not in seen or c.id > seen[key].id:
            seen[key] = c

    # Группируем по типу
    grouped = {}
    for c in seen.values():
        grouped.setdefault(c.component_type, []).append(c)

    # Словарь моделей и русских названий
    component_meta = [
        ('engine', 'Двигатели', '⚙️', Engine),
        ('transmission', 'КПП', '🔧', Transmission),
        ('differential', 'Редукторы', '⚙️', Differential),
        ('suspension', 'Подвеска', '🔩', Suspension),
        ('brakes', 'Тормоза', '🛑', Brake),
        ('cooling', 'Охлаждение', '❄️', Cooling),
        ('electronics', 'Электроника', '⚡', Electronics),
        ('ecu', 'ЭБУ', '🧠', ECU),
        ('turbo', 'Турбины', '🌀', Turbo),
        ('intercooler', 'Интеркулеры', '🌬️', Intercooler),
        ('exhaust', 'Выхлоп', '💨', Exhaust),
    ]

        # Обогащаем данными
    sections = []
    for type_key, label, icon, cls in component_meta:
        if type_key not in grouped:
            continue
        items = []
        for c in grouped[type_key]:
            obj = cls.query.get(c.component_id)
            if not obj:
                continue
            items.append({
                'obj': obj,
                'status': c.status,
                'description': c.description,
                'estimated_cost': c.estimated_cost,
                'difficulty': c.difficulty,
                'source': c.source,
            })
        # ← ВАЖНО: if items и sections.append — ВНЕ цикла for c
        if items:
            sections.append({
                'type': type_key,
                'label': label,
                'icon': icon,
                'entries': items,
            })

    # Свапы (двигатели)
    raw_swaps = Swap.query.filter_by(
        source_vehicle_model_id=model_id,
        source_component_type='engine'
    ).all()
    swaps = []
    for s in raw_swaps:
        src = Engine.query.get(s.source_component_id)
        tgt = Engine.query.get(s.target_component_id)
        swaps.append({
            'swap': s,
            'source_engine': src.name if src else '?',
            'source_hp': src.power_hp if src else '?',
            'target_engine': tgt.name if tgt else '?',
            'target_hp': tgt.power_hp if tgt else '?',
            'modifications': json.loads(s.required_modifications) if s.required_modifications else [],
            'parts': json.loads(s.required_parts) if s.required_parts else [],
        })

    title = f"{model.brand.name} {model.name} ({model.generation}) — характеристики и совместимые компоненты"
    description = f"Автомобиль {model.brand.name} {model.name} {model.generation}. Кузов: {model.body_type}. Годы выпуска: {model.year_start}–{model.year_end}. Совместимые двигатели, КПП, подвеска, тормоза и свапы на AutoForge."
    return render_template('model_detail.html',
                           model=model,
                           sections=sections,
                           swaps=swaps,
                           title=title,
                           description=description)
