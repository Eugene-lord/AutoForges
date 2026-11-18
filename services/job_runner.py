"""
Простой фоновый раннер задач.
Использует потоки Python (threading).
Для MVP достаточно. При росте нагрузки — заменить на Celery + Redis
без изменения логики вызывающего кода.
"""
import json
import threading
import traceback
from datetime import datetime, timezone
from extensions import db


def run_job_async(app, job_id: int):
    """
    Запускает задачу в фоновом потоке.
    app — Flask application (нужен для app_context в потоке).
    job_id — ID записи GenerationJob.
    """
    thread = threading.Thread(
        target=_run_job,
        args=(app, job_id),
        daemon=True
    )
    thread.start()
    return thread


def _run_job(app, job_id: int):
    """Выполняет задачу внутри app_context."""
    from models import GenerationJob
    from services import generation_service

    with app.app_context():
        job = GenerationJob.query.get(job_id)
        if not job:
            return

        job.status = 'running'
        job.started_at = datetime.now(timezone.utc)()
        db.session.commit()

        try:
            params = json.loads(job.params_json) if job.params_json else {}
            result = _dispatch_job(job.job_type, params, generation_service)

            job.status = 'done'
            job.result_json = json.dumps(result, ensure_ascii=False, default=str)
            job.started_at = datetime.now(timezone.utc)()
            job.finished_at = ()
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            job = GenerationJob.query.get(job_id)
            if job:
                job.status = 'failed'
                job.error = f"{e}\n{traceback.format_exc()}"
                job.started_at = datetime.now(timezone.utc)()
                job.finished_at = ()
                db.session.commit()


def _dispatch_job(job_type: str, params: dict, gs) -> dict:
    """
    Роутинг задач по типу.
    Пока все функции-заготовки возвращают пустой список
    (когда ИИ подключится — будут вызывать AI Provider).
    """
    if job_type == 'generate_brands':
        # В будущем: вызвать AI Provider, получить список брендов,
        # для каждого вызвать find_or_create_brand.
        return {'created': [], 'note': 'AI не подключён'}

    elif job_type == 'generate_models':
        brand_id = params.get('brand_id')
        # В будущем: AI Provider → модели → find_or_create_model
        return {'brand_id': brand_id, 'created': [], 'note': 'AI не подключён'}

    elif job_type == 'generate_generations':
        model_id = params.get('model_id')
        # В будущем: AI Provider → поколения → find_or_create_generation
        return {'model_id': model_id, 'created': [], 'note': 'AI не подключён'}

    elif job_type == 'generate_components':
        model_id = params.get('model_id')
        component_type = params.get('component_type')
        # В будущем: AI Provider → компоненты → find_or_create_component
        return {'model_id': model_id, 'component_type': component_type,
                'created': [], 'note': 'AI не подключён'}

    elif job_type == 'generate_variants':
        component_type = params.get('component_type')
        component_id = params.get('component_id')
        # В будущем: AI Provider → варианты → find_or_create_variant
        return {'component_type': component_type, 'component_id': component_id,
                'created': [], 'note': 'AI не подключён'}

    elif job_type == 'generate_applications':
        model_id = params.get('model_id')
        # В будущем: AI Provider → применения → find_or_create_application
        return {'model_id': model_id, 'created': [], 'note': 'AI не подключён'}

    elif job_type == 'update_coverage':
        model_id = params.get('model_id')
        if model_id:
            cov = gs.calculate_model_coverage(model_id)
            gs.update_coverage('model', model_id, cov['level'], cov['details'])
            db.session.commit()
            return {'model_id': model_id, 'level': cov['level']}
        return {'note': 'model_id не указан'}

    else:
        raise ValueError(f"Неизвестный job_type: {job_type}")


def enqueue_job(app, job_type: str, params: dict = None) -> int:
    """
    Создаёт GenerationJob и запускает его в фоне.
    Возвращает ID задачи.
    """
    from models import GenerationJob

    with app.app_context():
        job = GenerationJob(
            job_type=job_type,
            params_json=json.dumps(params, ensure_ascii=False) if params else None,
            status='pending',
            created_at=datetime.now(timezone.utc)()()
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    run_job_async(app, job_id)
    return job_id