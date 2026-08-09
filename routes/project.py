from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, SwapProject, Comment, Favorite
import json

project_bp = Blueprint('project', __name__, url_prefix='/project')

@project_bp.route('/<int:project_id>')
def view(project_id):
    project = SwapProject.query.get_or_404(project_id)
    # Показываем только публичные или свои проекты
    if not project.is_public and (not current_user.is_authenticated or project.user_id != current_user.id):
        flash('Проект недоступен', 'danger')
        return redirect(url_for('community.index'))
    vehicle = project.vehicle
    config = json.loads(project.configuration_json)
    comments = Comment.query.filter_by(project_id=project_id).order_by(Comment.created_at.asc()).all()
    # Проверим, в избранном ли у текущего пользователя
    is_favorited = False
    if current_user.is_authenticated:
        fav = Favorite.query.filter_by(user_id=current_user.id, project_id=project_id).first()
        is_favorited = fav is not None
    return render_template('project_detail.html', project=project, vehicle=vehicle, config=config,
                           comments=comments, is_favorited=is_favorited)

@project_bp.route('/<int:project_id>/comment', methods=['POST'])
@login_required
def add_comment(project_id):
    project = SwapProject.query.get_or_404(project_id)
    if not project.is_public and project.user_id != current_user.id:
        flash('Нельзя комментировать этот проект', 'danger')
        return redirect(url_for('project.view', project_id=project_id))
    text = request.form.get('comment_text', '').strip()
    if text:
        comment = Comment(user_id=current_user.id, project_id=project_id, text=text)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен', 'success')
    return redirect(url_for('project.view', project_id=project_id))

@project_bp.route('/<int:project_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(project_id):
    project = SwapProject.query.get_or_404(project_id)
    if not project.is_public and project.user_id != current_user.id:
        flash('Нельзя добавить в избранное этот проект', 'danger')
        return redirect(url_for('project.view', project_id=project_id))
    fav = Favorite.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    if fav:
        db.session.delete(fav)
        flash('Удалено из избранного', 'info')
    else:
        fav = Favorite(user_id=current_user.id, project_id=project_id)
        db.session.add(fav)
        flash('Добавлено в избранное', 'success')
    db.session.commit()
    return redirect(url_for('project.view', project_id=project_id))

@project_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    project = SwapProject.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('project.view', project_id=project_id))
    if request.method == 'POST':
        project.name = request.form.get('name', 'Без названия')
        project.is_public = request.form.get('is_public') == 'on'
        db.session.commit()
        flash('Проект обновлён', 'success')
        return redirect(url_for('project.view', project_id=project_id))
    return render_template('edit_project.html', project=project)
