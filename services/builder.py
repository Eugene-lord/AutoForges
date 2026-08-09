from flask import session
from models import (Model, Engine, Transmission, Differential, Suspension,
                    Brake, Cooling, Electronics, ECU, Turbo, Intercooler, Exhaust,
                    ElectricMotor, Battery, Inverter,
                    SwapProject, Compatibility, ShopLink)
from extensions import db
import json

BUILDER_SESSION_KEY = 'builder_selections'

COMPONENT_MODELS = {
    'engine': Engine,
    'transmission': Transmission,
    'differential': Differential,
    'suspension': Suspension,
    'brakes': Brake,
    'cooling': Cooling,
    'electronics': Electronics,
    'ecu': ECU,
    'turbo': Turbo,
    'intercooler': Intercooler,
    'exhaust': Exhaust,
    # новые типы для электро/гибридов
    'electric_motor': ElectricMotor,
    'battery': Battery,
    'inverter': Inverter,
}

def init_builder():
    if BUILDER_SESSION_KEY not in session:
        session[BUILDER_SESSION_KEY] = {}

def set_vehicle(model_id):
    model = Model.query.get(model_id)
    if not model:
        return None
    session[BUILDER_SESSION_KEY]['vehicle'] = {
        'id': model.id,
        'name': f"{model.brand.name} {model.name} ({model.generation})",
        'year': f"{model.year_start}–{model.year_end}"
    }
    session.modified = True
    return model

def get_vehicle():
    return session.get(BUILDER_SESSION_KEY, {}).get('vehicle')

def get_compatible_components(vehicle_model_id, component_type):
    comp_rows = Compatibility.query.filter_by(
        vehicle_model_id=vehicle_model_id,
        component_type=component_type
    ).all()
    result = []
    model_class = COMPONENT_MODELS.get(component_type)
    if not model_class:
        return result
    for comp in comp_rows:
        item = model_class.query.get(comp.component_id)
        if item:
            result.append({
                'item': item,
                'status': comp.status,
                'description': comp.description,
                'estimated_cost': comp.estimated_cost,
                'difficulty': comp.difficulty,
                'compatibility_id': comp.id
            })
    return result

def set_component(component_type, item_id):
    model_class = COMPONENT_MODELS.get(component_type)
    if not model_class:
        return None
    item = model_class.query.get(item_id)
    if not item:
        return None
    data = {'id': item.id, 'name': item.name}
    # поля для разных типов
    if component_type == 'engine':
        data.update({'displacement': item.displacement, 'power_hp': item.power_hp, 'torque_nm': item.torque_nm})
    elif component_type == 'transmission':
        data.update({'type': item.type, 'gears': item.gears})
    elif component_type == 'differential':
        data.update({'type': item.type, 'ratio': item.ratio})
    elif component_type == 'suspension':
        data.update({'type': item.type})
    elif component_type == 'brakes':
        data.update({'type': item.type, 'size': item.size})
    elif component_type == 'cooling':
        data.update({'type': item.type})
    elif component_type == 'electronics':
        data.update({'description': item.description})
    elif component_type == 'ecu':
        data.update({'type': item.type})
    elif component_type == 'turbo':
        data.update({'pressure': item.pressure})
    elif component_type == 'intercooler':
        data.update({'type': item.type})
    elif component_type == 'exhaust':
        data.update({'material': item.material})
    elif component_type == 'electric_motor':
        data.update({'power_hp': item.power_hp, 'torque_nm': item.torque_nm, 'motor_type': item.motor_type})
    elif component_type == 'battery':
        data.update({'capacity_kwh': item.capacity_kwh, 'voltage': item.voltage, 'battery_type': item.battery_type})
    elif component_type == 'inverter':
        data.update({'power_kw': item.power_kw, 'inverter_type': item.inverter_type})
    session[BUILDER_SESSION_KEY][component_type] = data
    session.modified = True
    return item

def get_component(component_type):
    return session.get(BUILDER_SESSION_KEY, {}).get(component_type)

def clear_builder():
    session.pop(BUILDER_SESSION_KEY, None)

def get_summary():
    selections = session.get(BUILDER_SESSION_KEY, {})
    vehicle = selections.get('vehicle')
    if not vehicle:
        return None
    total_cost = 0
    max_difficulty = 0
    components_list = []
    for comp_type, comp_data in selections.items():
        if comp_type == 'vehicle' or not isinstance(comp_data, dict):
            continue
        compatibility = Compatibility.query.filter_by(
            vehicle_model_id=vehicle['id'],
            component_type=comp_type,
            component_id=comp_data['id']
        ).first()
        if compatibility:
            total_cost += compatibility.estimated_cost or 0
            if compatibility.difficulty and compatibility.difficulty > max_difficulty:
                max_difficulty = compatibility.difficulty
            components_list.append({
                'type': comp_type,
                'name': comp_data['name'],
                'cost': compatibility.estimated_cost or 0,
                'difficulty': compatibility.difficulty or 0,
                'status': compatibility.status,
                'description': compatibility.description,
                'compatibility_id': compatibility.id
            })
    return {
        'total_cost': total_cost,
        'max_difficulty': max_difficulty,
        'components': components_list
    }

def save_project(name, user_id, is_public=False):
    selections = session.get(BUILDER_SESSION_KEY, {})
    vehicle = selections.get('vehicle')
    if not vehicle or not user_id:
        return None
    config = {k: v for k, v in selections.items() if k != 'vehicle'}
    summary = get_summary()
    project = None
    try:
        project = SwapProject(
            user_id=user_id,
            name=name,
            vehicle_model_id=vehicle['id'],
            configuration_json=json.dumps(config, ensure_ascii=False),
            total_cost=summary['total_cost'] if summary else 0,
            difficulty=summary['max_difficulty'] if summary else 0,
            is_public=is_public
        )
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка сохранения проекта: {e}")
        return None
    return project

def get_shop_prices(compatibility_id):
    links = ShopLink.query.filter_by(compatibility_id=compatibility_id).all()
    result = []
    for link in links:
        result.append({
            'shop_name': link.shop.name,
            'price': link.price,
            'currency': link.currency,
            'url': link.url,
            'in_stock': link.in_stock
        })
    return result
