from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    country = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(300), nullable=True)
    models = db.relationship('Model', backref='brand', lazy='dynamic')

class Model(db.Model):
    __tablename__ = 'models'
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    generation = db.Column(db.String(100), nullable=True)
    year_start = db.Column(db.Integer, nullable=True)
    year_end = db.Column(db.Integer, nullable=True)
    body_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    engines = db.relationship('Engine', backref='model', lazy='dynamic')

class Engine(db.Model):
    __tablename__ = 'engines'
    id = db.Column(db.Integer, primary_key=True)
    engine_code = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    displacement = db.Column(db.Float, nullable=True)
    power_hp = db.Column(db.Integer, nullable=True)
    torque_nm = db.Column(db.Integer, nullable=True)
    fuel_type = db.Column(db.String(30), nullable=True)
    configuration = db.Column(db.String(50), nullable=True)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=True)

class Transmission(db.Model):
    __tablename__ = 'transmissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50))
    gears = db.Column(db.Integer)

class Differential(db.Model):
    __tablename__ = 'differentials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50))
    ratio = db.Column(db.Float)

class Suspension(db.Model):
    __tablename__ = 'suspensions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50))

class Brake(db.Model):
    __tablename__ = 'brakes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50))
    size = db.Column(db.String(50))

class Cooling(db.Model):
    __tablename__ = 'coolings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50))

class Electronics(db.Model):
    __tablename__ = 'electronics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

class ECU(db.Model):
    __tablename__ = 'ecus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50))

class Turbo(db.Model):
    __tablename__ = 'turbos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    pressure = db.Column(db.String(50))

class Intercooler(db.Model):
    __tablename__ = 'intercoolers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50))

class Exhaust(db.Model):
    __tablename__ = 'exhausts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    material = db.Column(db.String(50))

# --- Электромобильные компоненты ---
class ElectricMotor(db.Model):
    __tablename__ = 'electric_motors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    power_hp = db.Column(db.Integer, nullable=True)
    torque_nm = db.Column(db.Integer, nullable=True)
    motor_type = db.Column(db.String(50), nullable=True)  # синхронный, асинхронный

class Battery(db.Model):
    __tablename__ = 'batteries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    capacity_kwh = db.Column(db.Float, nullable=True)
    voltage = db.Column(db.Float, nullable=True)
    battery_type = db.Column(db.String(50), nullable=True)  # Li-Ion, LiFePO4

class Inverter(db.Model):
    __tablename__ = 'inverters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    power_kw = db.Column(db.Float, nullable=True)
    inverter_type = db.Column(db.String(50), nullable=True)
# --------------------------------

class Compatibility(db.Model):
    __tablename__ = 'compatibilities'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    component_type = db.Column(db.String(50), nullable=False)
    component_id = db.Column(db.Integer, nullable=False)
    # Существующее поле для совместимости (compatible, warning, incompatible)
    status = db.Column(db.String(20), nullable=False, default='compatible')
    description = db.Column(db.Text, nullable=True)
    estimated_cost = db.Column(db.Float, nullable=True)
    difficulty = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Новые поля для AI-метаданных
    knowledge_status = db.Column(db.String(20), default='VERIFIED')  # VERIFIED, REVIEW_REQUIRED, AI_GENERATED, REJECTED
    source = db.Column(db.String(50), default='manual')  # manual, ai_deepseek, ai_gigachat, user_submitted
    confidence = db.Column(db.Float, nullable=True)       # 0.0 - 1.0
    risk_level = db.Column(db.String(10), default='LOW')  # LOW, MEDIUM, HIGH
    verified_by = db.Column(db.Integer, nullable=True)    # ID пользователя-администратора
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('vehicle_model_id', 'component_type', 'component_id', name='uix_comp'),
    )

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class SwapProject(db.Model):
    __tablename__ = 'swap_projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    vehicle_model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    configuration_json = db.Column(db.Text, nullable=False)
    total_cost = db.Column(db.Float, nullable=True)
    difficulty = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='projects')
    vehicle = db.relationship('Model')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('swap_projects.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
    project = db.relationship('SwapProject', backref='comments')

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('swap_projects.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='favorites')
    project = db.relationship('SwapProject', backref='favorited_by')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'project_id', name='uix_user_project'),
    )

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    logo_url = db.Column(db.String(300), nullable=True)
    affiliate_code = db.Column(db.String(100), nullable=True)

class ShopLink(db.Model):
    __tablename__ = 'shop_links'
    id = db.Column(db.Integer, primary_key=True)
    compatibility_id = db.Column(db.Integer, db.ForeignKey('compatibilities.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    url = db.Column(db.String(500), nullable=True)
    in_stock = db.Column(db.Boolean, default=True)

    compatibility = db.relationship('Compatibility', backref='shop_links')
    shop = db.relationship('Shop', backref='shop_links')

class UserCar(db.Model):
    __tablename__ = 'user_cars'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    nickname = db.Column(db.String(100), nullable=True)

    user = db.relationship('User', backref='cars')
    model = db.relationship('Model')

class KnowledgeItem(db.Model):
    __tablename__ = 'knowledge_items'
    id = db.Column(db.Integer, primary_key=True)
    knowledge_type = db.Column(db.String(50), nullable=False)  # например: 'compatibility', 'swap', 'component_info'
    source = db.Column(db.String(50), default='ai')             # 'ai', 'user', 'manual'
    confidence = db.Column(db.Float, nullable=True)             # 0.0 - 1.0
    risk_level = db.Column(db.String(10), default='LOW')        # LOW, MEDIUM, HIGH
    status = db.Column(db.String(20), default='AI_GENERATED')   # AI_GENERATED, REVIEW_REQUIRED, VERIFIED, REJECTED
    data_json = db.Column(db.Text, nullable=True)               # JSON-строка с содержимым
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_by = db.Column(db.Integer, nullable=True)          # ID администратора
    verified_at = db.Column(db.DateTime, nullable=True)