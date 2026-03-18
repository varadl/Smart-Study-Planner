"""
Smart Study Planner - Authentication Routes
Handles user registration, login, and logout.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.db_setup import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Basic validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        hashed_pw = generate_password_hash(password)
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_pw)
            )
            db.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            flash('Username or email already exists.', 'danger')
        finally:
            db.close()

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('login.html')

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']  = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """View profile and change password."""
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('auth.login'))

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if request.method == 'POST':
        current_pw  = request.form.get('current_password', '').strip()
        new_pw      = request.form.get('new_password', '').strip()
        confirm_pw  = request.form.get('confirm_password', '').strip()

        if not current_pw or not new_pw or not confirm_pw:
            flash('All fields are required.', 'danger')
        elif not check_password_hash(user['password'], current_pw):
            flash('Current password is incorrect.', 'danger')
        elif len(new_pw) < 6:
            flash('New password must be at least 6 characters.', 'danger')
        elif new_pw != confirm_pw:
            flash('New passwords do not match.', 'danger')
        else:
            hashed = generate_password_hash(new_pw)
            db.execute('UPDATE users SET password = ? WHERE id = ?', (hashed, session['user_id']))
            db.commit()
            flash('Password changed successfully! 🎉', 'success')

    # Get account stats
    total_subjects = db.execute(
        'SELECT COUNT(*) FROM subjects WHERE user_id = ?', (session['user_id'],)
    ).fetchone()[0]
    total_tasks = db.execute('''
        SELECT COUNT(*) FROM tasks t
        JOIN subjects s ON t.subject_id = s.id
        WHERE s.user_id = ?
    ''', (session['user_id'],)).fetchone()[0]
    completed_tasks = db.execute('''
        SELECT COUNT(*) FROM tasks t
        JOIN subjects s ON t.subject_id = s.id
        WHERE s.user_id = ? AND t.status = 'Completed'
    ''', (session['user_id'],)).fetchone()[0]
    db.close()

    progress = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    return render_template('profile.html',
        user=user,
        total_subjects=total_subjects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        progress=progress
    )
