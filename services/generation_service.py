"""
Сервис генерации и поиска сущностей.
Пока без вызова ИИ — только логика работы с БД.
Когда ИИ подключится, эти функции будут вызываться после получения ответа от AI Provider.
"""
from models import (db, Brand, Model, Generation, Engine, Transmission,
                    Differential, Suspension, Brake, Cooling, Electronics,
                    ECU, Turbo, Intercooler, Exhaust, ComponentVariant,
                    Application, Source, SourceEvidence, CatalogCoverage)
from datetime import datetime, timezone

# Маппинг component_type → модель SQLAlchemy
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
}


def _normalize(name: str) -> str:
    """Нормализация имени для поиска дубликатов."""
    if not name:
        return ''
    return name.strip().lower().replace(' ', '').replace('-', '').replace('_', '')


# ---------- BRAND ----------
def find_or_create_brand(name: str, country: str = None, description: str = None) -> Brand:
    """
    Ищет бренд по нормализованному имени.
    Если найден — возвращает существующий (не дублирует).
    Если нет — создаёт новый.
    """
    norm = _normalize(name)
    for b in Brand.query.all():
        if _normalize(b.name) == norm:
            return b
    brand = Brand(name=name, country=country, description=description)
    db.session.add(brand)
    db.session.flush()
    return brand


# ---------- MODEL ----------
def find_or_create_model(brand_id: int, name: str, generation_str: str = None,
                         year_start: int = None, year_end: int = None,
                         body_type: str = None, description: str = None) -> Model:
    """Ищет модель по brand_id + нормализованному имени. Создаёт если нет."""
    norm = _normalize(name)
    for m in Model.query.filter_by(brand_id=brand_id).all():
        if _normalize(m.name) == norm:
            return m
    model = Model(
        brand_id=brand_id, name=name, generation=generation_str,
        year_start=year_start, year_end=year_end,
        body_type=body_type, description=description
    )
    db.session.add(model)
    db.session.flush()
    return model


# ---------- GENERATION ----------
def find_or_create_generation(model_id: int, name: str,
                              year_start: int = None, year_end: int = None,
                              body_types: str = None, markets: str = None,
                              description: str = None) -> Generation:
    """Ищет поколение по model_id + нормализованному имени. Создаёт если нет."""
    norm = _normalize(name)
    for g in Generation.query.filter_by(model_id=model_id).all():
        if _normalize(g.name) == norm:
            return g
    gen = Generation(
        model_id=model_id, name=name,
        year_start=year_start, year_end=year_end,
        body_types=body_types, markets=markets, description=description
    )
    db.session.add(gen)
    db.session.flush()
    return gen


# ---------- COMPONENTS (универсально) ----------
def find_or_create_component(component_type: str, identifier: str, **kwargs):
    """
    Универсальная функция поиска/создания компонента.
    identifier — уникальное поле (engine_code для engine, name для остальных).
    kwargs — остальные поля модели (displacement, power_hp, type, и т.д.)
    """
    model_class = COMPONENT_MODELS.get(component_type)
    if not model_class:
        raise ValueError(f"Неизвестный component_type: {component_type}")

    # Для engine ищем по engine_code, для остальных — по name
    if component_type == 'engine':
        field = 'engine_code'
    else:
        field = 'name'

    norm = _normalize(identifier)
    for item in model_class.query.all():
        if _normalize(getattr(item, field, '')) == norm:
            return item

    # Создаём новую запись
    create_kwargs = {field: identifier}
    for k, v in kwargs.items():
        # Пропускаем поля, которых нет в модели
        if hasattr(model_class, k):
            create_kwargs[k] = v
    # Метаданные
    if hasattr(model_class, 'source'):
        create_kwargs.setdefault('source', 'manual')

    item = model_class(**create_kwargs)
    db.session.add(item)
    db.session.flush()
    return item


# ---------- COMPONENT VARIANT ----------
def find_or_create_variant(component_type: str, component_id: int,
                           variant_code: str, name: str = None,
                           market: str = None, year_start: int = None,
                           year_end: int = None, specs_json: str = None,
                           features: str = None) -> ComponentVariant:
    """Ищет вариант по component_type + component_id + variant_code. Создаёт если нет."""
    existing = ComponentVariant.query.filter_by(
        component_type=component_type,
        component_id=component_id,
        variant_code=variant_code
    ).first()
    if existing:
        return existing
    variant = ComponentVariant(
        component_type=component_type,
        component_id=component_id,
        variant_code=variant_code,
        name=name,
        market=market,
        year_start=year_start,
        year_end=year_end,
        specs_json=specs_json,
        features=features
    )
    db.session.add(variant)
    db.session.flush()
    return variant


# ---------- APPLICATION ----------
def find_or_create_application(vehicle_model_id: int, component_type: str,
                                component_id: int, application_type: str,
                                variant_id: int = None,
                                generation_id: int = None,
                                condition: str = None) -> Application:
    """Ищет применение. Создаёт если нет."""
    existing = Application.query.filter_by(
        vehicle_model_id=vehicle_model_id,
        component_type=component_type,
        component_id=component_id,
        variant_id=variant_id,
        application_type=application_type
    ).first()
    if existing:
        return existing
    app = Application(
        vehicle_model_id=vehicle_model_id,
        generation_id=generation_id,
        component_type=component_type,
        component_id=component_id,
        variant_id=variant_id,
        application_type=application_type,
        condition=condition
    )
    db.session.add(app)
    db.session.flush()
    return app


# ---------- SOURCE ----------
def find_or_create_source(source_type: str, url: str = None,
                          title: str = None, description: str = None,
                          reliability: str = 'medium') -> Source:
    """Ищет источник по URL. Создаёт если нет."""
    if url:
        existing = Source.query.filter_by(url=url).first()
        if existing:
            return existing
    source = Source(
        source_type=source_type,
        url=url,
        title=title,
        description=description,
        reliability=reliability
    )
    db.session.add(source)
    db.session.flush()
    return source


# ---------- CATALOG COVERAGE ----------
def update_coverage(entity_type: str, entity_id: int, level: str,
                    details_json: str = None):
    """Обновляет или создаёт запись о полноте каталога."""
    existing = CatalogCoverage.query.filter_by(
        entity_type=entity_type, entity_id=entity_id
    ).first()
    if existing:
        existing.level = level
        existing.details_json = details_json
        existing.updated_at = datetime.now(timezone.utc)()
    else:
        cov = CatalogCoverage(
            entity_type=entity_type,
            entity_id=entity_id,
            level=level,
            details_json=details_json
        )
        db.session.add(cov)
    db.session.flush()


def calculate_model_coverage(model_id: int) -> dict:
    """
    Считает полноту каталога для модели:
    сколько компонентов каждого типа привязано (через Application или Compatibility).
    Возвращает dict с level и details.
    """
    from models import Compatibility

    counts = {}
    for ct in COMPONENT_MODELS.keys():
        app_count = Application.query.filter_by(
            vehicle_model_id=model_id, component_type=ct
        ).count()
        comp_count = Compatibility.query.filter_by(
            vehicle_model_id=model_id, component_type=ct
        ).count()
        counts[ct] = app_count + comp_count

    total = sum(counts.values())
    present = sum(1 for v in counts.values() if v > 0)
    total_types = len(counts)

    if present == 0:
        level = 'empty'
    elif present < total_types * 0.5:
        level = 'partial'
    elif present < total_types:
        level = 'partial'
    else:
        level = 'full'

    missing = [ct for ct, v in counts.items() if v == 0]
    details = {
        'counts': counts,
        'missing': missing,
        'total_components': total,
        'types_present': present,
        'types_total': total_types,
    }
    import json
    return {'level': level, 'details': json.dumps(details, ensure_ascii=False)}