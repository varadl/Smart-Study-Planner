"""
Smart Study Planner - Planner Routes
Generates and displays the smart day-wise study plan.
"""
from flask import Blueprint, render_template, redirect, url_for, session, flash
from models.db_setup import get_db
from datetime import date, timedelta
import math

planner_bp = Blueprint('planner', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@planner_bp.route('/plan')
@login_required
def study_plan():
    """Display the generated study plan."""
    db = get_db()

    # Fetch plan entries with task and subject info
    plan_entries = db.execute('''
        SELECT sp.date, t.topic_name, t.status, s.subject_name, sp.task_id
        FROM study_plan sp
        JOIN tasks    t  ON sp.task_id    = t.id
        JOIN subjects s  ON t.subject_id  = s.id
        WHERE sp.user_id = ?
        ORDER BY sp.date, s.subject_name
    ''', (session['user_id'],)).fetchall()

    db.close()

    # Group plan by date
    plan_by_date = {}
    for entry in plan_entries:
        entry_date = entry['date']
        if entry_date not in plan_by_date:
            plan_by_date[entry_date] = []
        plan_by_date[entry_date].append(entry)

    return render_template('study_plan.html', plan_by_date=plan_by_date)


@planner_bp.route('/plan/generate', methods=['POST'])
@login_required
def generate_plan():
    """
    Smart Plan Generation Algorithm:
    - For each subject, compute days remaining until exam date.
    - Fetch all pending tasks for that subject.
    - Distribute tasks evenly across available days (at least 1 task/day).
    - Store the result in study_plan table.
    """
    user_id = session['user_id']
    today   = date.today()
    db      = get_db()

    # Clear old plan for this user
    db.execute('DELETE FROM study_plan WHERE user_id = ?', (user_id,))
    db.commit()

    # Get all subjects for user
    subjects = db.execute(
        'SELECT * FROM subjects WHERE user_id = ? ORDER BY exam_date',
        (user_id,)
    ).fetchall()

    if not subjects:
        flash('No subjects found. Please add subjects first.', 'warning')
        db.close()
        return redirect(url_for('planner.study_plan'))

    plan_entries = []

    for subj in subjects:
        exam_date = date.fromisoformat(subj['exam_date'])
        days_left = (exam_date - today).days

        if days_left <= 0:
            # Exam already passed – skip or assign to today
            days_left = 1

        # Fetch pending tasks for this subject
        pending_tasks = db.execute(
            "SELECT * FROM tasks WHERE subject_id = ? AND status = 'Pending'",
            (subj['id'],)
        ).fetchall()

        if not pending_tasks:
            continue

        total_tasks    = len(pending_tasks)
        # Tasks per day (spread evenly; minimum 1)
        tasks_per_day  = max(1, math.ceil(total_tasks / days_left))

        task_index = 0
        day_offset = 0

        while task_index < total_tasks:
            plan_date = today + timedelta(days=day_offset)

            # Don't schedule beyond the exam date
            if plan_date >= exam_date:
                plan_date = exam_date - timedelta(days=1)

            # Assign tasks_per_day tasks to this day
            for _ in range(tasks_per_day):
                if task_index >= total_tasks:
                    break
                plan_entries.append((
                    user_id,
                    plan_date.isoformat(),
                    pending_tasks[task_index]['id']
                ))
                task_index += 1

            day_offset += 1

    if plan_entries:
        db.executemany(
            'INSERT INTO study_plan (user_id, date, task_id) VALUES (?, ?, ?)',
            plan_entries
        )
        db.commit()
        flash('Study plan generated successfully! 🎉', 'success')
    else:
        flash('No pending tasks found to plan. Add tasks to your subjects first.', 'warning')

    db.close()
    return redirect(url_for('planner.study_plan'))
