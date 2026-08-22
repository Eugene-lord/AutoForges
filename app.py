from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from models import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.main import main_bp
    app.register_blueprint(main_bp)

    from routes.catalog import catalog_bp
    app.register_blueprint(catalog_bp)

    from routes.builder import builder_bp
    app.register_blueprint(builder_bp)

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    from routes.community import community_bp
    app.register_blueprint(community_bp)

    from routes.project import project_bp
    app.register_blueprint(project_bp)

    from routes.search import search_bp
    app.register_blueprint(search_bp)

    from routes.knowledge import knowledge_bp
    app.register_blueprint(knowledge_bp)

    from routes.ai import ai_bp
    app.register_blueprint(ai_bp)

    from routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    with app.app_context():
        from seed_data import seed
        seed()

        # Временный маршрут для заполнения базы (удалить после использования!)
    @app.route('/seed-db-2024')
    def seed_db():
        from seed_data import seed
        seed()
        return 'База данных заполнена!'    

        # Временный маршрут для тестирования Knowledge Service
    
        # Временный маршрут для резервного копирования БД (удалить после использования!)
    @app.route('/backup-db')
    def backup_db():
        import subprocess, os
        try:
            # Выполняем pg_dump и возвращаем вывод
            result = subprocess.run(
                ['pg_dump', os.environ.get('DATABASE_URL', '')],
                capture_output=True, text=True, check=True
            )
            return f"<pre>{result.stdout}</pre>"
        except subprocess.CalledProcessError as e:
            return f"Ошибка pg_dump: {e.stderr}", 500
        except FileNotFoundError:
            return "pg_dump не найден на сервере.", 500

    return app
