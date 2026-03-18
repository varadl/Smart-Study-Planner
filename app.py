"""
Smart Study Planner - Main Flask Application Entry Point
Run with: python app.py
"""
import os
from flask import Flask, render_template, session, redirect, url_for
from models.db_setup import init_db
from routes.auth    import auth_bp
from routes.subject import subject_bp
from routes.task    import task_bp
from routes.planner import planner_bp

# ─── App Configuration ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ssp_super_secret_key_2024')

# ─── Register Blueprints ──────────────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(subject_bp)
app.register_blueprint(task_bp)
app.register_blueprint(planner_bp)


# ─── Core Routes ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Landing page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard – requires login."""
    if 'user_id' not in session:
        from flask import flash
        flash('Please log in to view the dashboard.', 'warning')
        return redirect(url_for('auth.login'))

    from models.db_setup import get_db
    from datetime import date

    user_id = session['user_id']
    db      = get_db()

    # Statistics
    total_subjects  = db.execute(
        'SELECT COUNT(*) FROM subjects WHERE user_id = ?', (user_id,)
    ).fetchone()[0]

    total_tasks     = db.execute('''
        SELECT COUNT(*) FROM tasks t
        JOIN subjects s ON t.subject_id = s.id
        WHERE s.user_id = ?
    ''', (user_id,)).fetchone()[0]

    completed_tasks = db.execute('''
        SELECT COUNT(*) FROM tasks t
        JOIN subjects s ON t.subject_id = s.id
        WHERE s.user_id = ? AND t.status = 'Completed'
    ''', (user_id,)).fetchone()[0]

    progress = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    # Today's scheduled tasks
    today_str   = date.today().isoformat()
    today_tasks = db.execute('''
        SELECT t.topic_name, t.status, s.subject_name
        FROM study_plan sp
        JOIN tasks    t ON sp.task_id    = t.id
        JOIN subjects s ON t.subject_id  = s.id
        WHERE sp.user_id = ? AND sp.date = ?
        ORDER BY s.subject_name
    ''', (user_id, today_str)).fetchall()

    # Recent subjects with days-left
    subjects = db.execute(
        'SELECT * FROM subjects WHERE user_id = ? ORDER BY exam_date LIMIT 5',
        (user_id,)
    ).fetchall()

    db.close()

    today = date.today()
    subjects_with_days = []
    for s in subjects:
        exam = date.fromisoformat(s['exam_date'])
        days_left = (exam - today).days
        subjects_with_days.append({
            'subject_name': s['subject_name'],
            'exam_date':    s['exam_date'],
            'days_left':    days_left
        })

    return render_template(
        'dashboard.html',
        total_subjects  = total_subjects,
        total_tasks     = total_tasks,
        completed_tasks = completed_tasks,
        progress        = progress,
        today_tasks     = today_tasks,
        subjects        = subjects_with_days
    )


# ─── Initialise DB & Run ──────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("🚀 Smart Study Planner running at http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
