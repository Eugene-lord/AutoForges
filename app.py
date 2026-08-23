from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from models import User
from extensions import db, migrate, login_manager, limiter
from extensions import db, migrate, login_manager, limiter, csrf
from flask import Flask, render_template

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) 
    limiter.init_app(app)
    csrf.init_app(app)

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

    from routes.seo import seo_bp
    app.register_blueprint(seo_bp)

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
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app
