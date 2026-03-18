"""
Smart Study Planner - Subject Routes
Handles adding, viewing, and deleting subjects.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db_setup import get_db

subject_bp = Blueprint('subject', __name__)


def login_required(f):
    """Decorator to protect routes from unauthenticated access."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@subject_bp.route('/subjects')
@login_required
def subjects():
    """List all subjects for the current user."""
    from datetime import date
    db = get_db()
    rows = db.execute(
        'SELECT * FROM subjects WHERE user_id = ? ORDER BY exam_date',
        (session['user_id'],)
    ).fetchall()
    db.close()

    today = date.today()
    all_subjects = []
    for s in rows:
        exam = date.fromisoformat(s['exam_date'])
        days_left = (exam - today).days
        all_subjects.append({
            'id':           s['id'],
            'subject_name': s['subject_name'],
            'exam_date':    s['exam_date'],
            'days_left':    days_left
        })
    return render_template('add_subject.html', subjects=all_subjects)


@subject_bp.route('/subjects/add', methods=['POST'])
@login_required
def add_subject():
    """Add a new subject."""
    subject_name = request.form.get('subject_name', '').strip()
    exam_date    = request.form.get('exam_date', '').strip()

    if not subject_name or not exam_date:
        flash('Subject name and exam date are required.', 'danger')
        return redirect(url_for('subject.subjects'))

    db = get_db()
    db.execute(
        'INSERT INTO subjects (user_id, subject_name, exam_date) VALUES (?, ?, ?)',
        (session['user_id'], subject_name, exam_date)
    )
    db.commit()
    db.close()
    flash(f'Subject "{subject_name}" added successfully!', 'success')
    return redirect(url_for('subject.subjects'))


@subject_bp.route('/subjects/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    """Delete a subject and its tasks."""
    db = get_db()
    # Verify subject belongs to current user
    subj = db.execute(
        'SELECT * FROM subjects WHERE id = ? AND user_id = ?',
        (subject_id, session['user_id'])
    ).fetchone()

    if subj:
        db.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
        db.commit()
        flash('Subject deleted successfully.', 'success')
    else:
        flash('Subject not found or access denied.', 'danger')
    db.close()
    return redirect(url_for('subject.subjects'))
