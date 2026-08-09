from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, SwapProject, Model, Favorite, UserCar, Brand
import json

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def index():
    projects = SwapProject.query.filter_by(user_id=current_user.id).order_by(SwapProject.created_at.desc()).all()
    cars = UserCar.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', projects=projects, cars=cars)

@profile_bp.route('/projects')
@login_required
def projects():
    projects = SwapProject.query.filter_by(user_id=current_user.id).order_by(SwapProject.created_at.desc()).all()
    return render_template('projects.html', projects=projects)

@profile_bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = SwapProject.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('profile.projects'))
    vehicle = project.vehicle
    config = json.loads(project.configuration_json)
    return render_template('project_detail.html', project=project, vehicle=vehicle, config=config)

@profile_bp.route('/favorites')
@login_required
def favorites():
    favs = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    projects = [fav.project for fav in favs if fav.project is not None]
    return render_template('favorites.html', projects=projects)

@profile_bp.route('/garage')
@login_required
def garage():
    cars = UserCar.query.filter_by(user_id=current_user.id).all()
    return render_template('garage.html', cars=cars)

@profile_bp.route('/add-car', methods=['GET', 'POST'])
@login_required
def add_car():
    if request.method == 'POST':
        model_id = request.form.get('model_id', type=int)
        year = request.form.get('year', type=int)
        nickname = request.form.get('nickname', '')
        if not model_id:
            flash('Выберите модель автомобиля', 'danger')
            return redirect(url_for('profile.add_car'))
        car = UserCar(user_id=current_user.id, model_id=model_id, year=year, nickname=nickname)
        db.session.add(car)
        db.session.commit()
        flash('Автомобиль добавлен в гараж!', 'success')
        return redirect(url_for('profile.garage'))
    brands = Brand.query.all()
    return render_template('add_car.html', brands=brands)

@profile_bp.route('/start-project/<int:car_id>')
@login_required
def start_project(car_id):
    car = UserCar.query.get_or_404(car_id)
    if car.user_id != current_user.id:
        flash('Нет доступа', 'danger')
        return redirect(url_for('profile.garage'))
    from services.builder import set_vehicle
    set_vehicle(car.model_id)
    flash(f'Начат проект для {car.model.brand.name} {car.model.name}', 'info')
    return redirect(url_for('builder.index'))
