from app import create_app
from extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Создаём таблицы (если ещё не созданы)
        db.create_all()
        # Запускаем seed
        from seed_data import seed
        seed()
    app.run(debug=True)
