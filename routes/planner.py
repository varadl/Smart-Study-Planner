"""
Smart Study Planner - Planner Routes
Generates and displays the smart day-wise study plan.
"""
from flask import Blueprint, render_template, redirect, url_for, session, flash
from models.db_setup import get_db
from datetime import date, timedelta
import sqlite3
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
    try:
        # Fetch plan entries with task and subject info
        plan_entries = db.execute('''
            SELECT sp.date, t.topic_name, t.status, s.subject_name, sp.task_id
            FROM study_plan sp
            JOIN tasks    t  ON sp.task_id    = t.id
            JOIN subjects s  ON t.subject_id  = s.id
            WHERE sp.user_id = ?
            ORDER BY sp.date, s.subject_name
        ''', (session['user_id'],)).fetchall()
    except sqlite3.Error as e:
        flash(f'Error loading study plan: {e}', 'danger')
        plan_entries = []
    finally:
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
    Priority-Based Smart Plan Generation Algorithm:
    - Calculates dynamic priority score: (Difficulty * Remaining Tasks) / Days Left
    - Allocates tasks day-by-day up to a maximum daily bandwidth.
    """
    import math
    from collections import defaultdict
    from datetime import timedelta

    user_id = session['user_id']
    today   = date.today()
    db      = get_db()

    try:
        # Clear old plan for this user
        db.execute('DELETE FROM study_plan WHERE user_id = ?', (user_id,))
        db.commit()

        # Get all subjects for user
        subjects_records = db.execute(
            'SELECT * FROM subjects WHERE user_id = ? ORDER BY exam_date',
            (user_id,)
        ).fetchall()

        if not subjects_records:
            flash('No subjects found. Please add subjects first.', 'warning')
            return redirect(url_for('planner.study_plan'))

        # Load subjects and tasks into memory for simulation
        subjects_sim = []
        
        for subj in subjects_records:
            pending_tasks = db.execute(
                "SELECT id FROM tasks WHERE subject_id = ? AND status = 'Pending'",
                (subj['id'],)
            ).fetchall()
            
            exam_date = date.fromisoformat(subj['exam_date'])
            
            subjects_sim.append({
                'subject_id': subj['id'],
                'exam_date': exam_date,
                'difficulty': subj['difficulty'],
                'tasks': [t['id'] for t in pending_tasks]
            })

        plan_entries = []
        current_date = today
        max_tasks_per_day = 5  # Configurable daily bandwidth
        
        # Loop until all tasks are scheduled
        while any(len(s['tasks']) > 0 for s in subjects_sim):
            daily_assigned = 0
            
            # Calculate dynamic priority scores for the current day
            for s in subjects_sim:
                if len(s['tasks']) == 0:
                    s['priority_score'] = -1
                    continue
                    
                # Treat passed exams or exams today as '1 day left' to prevent division by zero
                days_left = max(1, (s['exam_date'] - current_date).days)
                s['priority_score'] = (s['difficulty'] * len(s['tasks'])) / days_left
                
            # Sort subjects by priority score descending
            subjects_sim.sort(key=lambda x: x['priority_score'], reverse=True)
            
            # Allocate tasks for 'current_date'
            for s in subjects_sim:
                if daily_assigned >= max_tasks_per_day:
                    break
                    
                if len(s['tasks']) > 0 and s['priority_score'] > -1:
                    tasks_to_take = min(
                        len(s['tasks']), 
                        max_tasks_per_day - daily_assigned
                    )
                    
                    for _ in range(tasks_to_take):
                        task_id = s['tasks'].pop(0)
                        plan_entries.append((
                            user_id,
                            current_date.isoformat(),
                            task_id
                        ))
                        daily_assigned += 1

            current_date += timedelta(days=1)
            
            # Failsafe limit
            if (current_date - today).days > 365 * 2:
                break

        if plan_entries:
            db.executemany(
                'INSERT INTO study_plan (user_id, date, task_id) VALUES (?, ?, ?)',
                plan_entries
            )
            db.commit()
            flash('Priority-based study plan generated successfully! 🎉', 'success')
        else:
            flash('No pending tasks found to plan. Add tasks to your subjects first.', 'warning')

    except sqlite3.Error as e:
        flash(f'Failed to generate plan due to a database error: {e}', 'danger')
    finally:
        db.close()

    return redirect(url_for('planner.study_plan'))
