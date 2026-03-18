"""
Smart Study Planner - Task Routes
Handles adding, completing, and deleting tasks/topics under subjects.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db_setup import get_db

task_bp = Blueprint('task', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@task_bp.route('/tasks')
@login_required
def tasks():
    """List all tasks grouped by subject for the current user."""
    db = get_db()
    # Fetch subjects belonging to user
    subjects = db.execute(
        'SELECT * FROM subjects WHERE user_id = ? ORDER BY exam_date',
        (session['user_id'],)
    ).fetchall()

    # Fetch tasks for each subject
    task_map = {}
    for subj in subjects:
        task_map[subj['id']] = db.execute(
            'SELECT * FROM tasks WHERE subject_id = ? ORDER BY id',
            (subj['id'],)
        ).fetchall()

    db.close()
    return render_template('add_task.html', subjects=subjects, task_map=task_map)


@task_bp.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    """Add a new topic to a subject."""
    subject_id = request.form.get('subject_id')
    topic_name = request.form.get('topic_name', '').strip()

    if not subject_id or not topic_name:
        flash('Subject and topic name are required.', 'danger')
        return redirect(url_for('task.tasks'))

    db = get_db()
    # Verify the subject belongs to the current user
    subj = db.execute(
        'SELECT * FROM subjects WHERE id = ? AND user_id = ?',
        (subject_id, session['user_id'])
    ).fetchone()

    if not subj:
        flash('Invalid subject.', 'danger')
        db.close()
        return redirect(url_for('task.tasks'))

    db.execute(
        'INSERT INTO tasks (subject_id, topic_name, status) VALUES (?, ?, ?)',
        (subject_id, topic_name, 'Pending')
    )
    db.commit()
    db.close()
    flash(f'Topic "{topic_name}" added successfully!', 'success')
    return redirect(url_for('task.tasks'))


@task_bp.route('/tasks/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    """Mark a task as Completed."""
    db = get_db()
    # Verify ownership through subjects join
    task = db.execute('''
        SELECT t.* FROM tasks t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.id = ? AND s.user_id = ?
    ''', (task_id, session['user_id'])).fetchone()

    if task:
        new_status = 'Completed' if task['status'] == 'Pending' else 'Pending'
        db.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
        db.commit()
        flash(f'Task marked as {new_status}.', 'success')
    else:
        flash('Task not found or access denied.', 'danger')

    db.close()
    return redirect(url_for('task.tasks'))


@task_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task/topic."""
    db = get_db()
    task = db.execute('''
        SELECT t.* FROM tasks t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.id = ? AND s.user_id = ?
    ''', (task_id, session['user_id'])).fetchone()

    if task:
        db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        db.commit()
        flash('Topic deleted successfully.', 'success')
    else:
        flash('Task not found or access denied.', 'danger')

    db.close()
    return redirect(url_for('task.tasks'))
