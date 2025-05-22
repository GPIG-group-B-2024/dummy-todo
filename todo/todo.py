from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)

@bp.route('/')
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT t.id, title, description, created, completed, due_date'
        ' FROM task t JOIN user u ON t.user_id = u.id'
        ' WHERE t.user_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('todo/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if g.user is None:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form.get('due_date') or None
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (title, description, user_id, due_date)'
                ' VALUES (?, ?, ?, ?)',
                (title, description, g.user['id'], due_date)
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')

def get_task(id, check_user=True):
    task = get_db().execute(
        'SELECT t.id, title, description, created, completed, due_date, user_id'
        ' FROM task t JOIN user u ON t.user_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_user and task['user_id'] != g.user['id']:
        abort(403)

    return task

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        due_date = request.form.get('due_date') or None
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET title = ?, description = ?, completed = ?, due_date = ?'
                ' WHERE id = ?',
                (title, description, completed, due_date, id)
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', task=task)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM task WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('todo.index'))
