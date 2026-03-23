import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if testuser exists by username
    cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        print(f"Testuser already exists with ID: {user_id}. Deleting existing data.")
        cursor.execute("DELETE FROM subjects WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM study_plan WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
    print("Creating testuser...")
    hashed_pw = generate_password_hash("password123")
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        ("testuser", "testuser@example.com", hashed_pw)
    )
    user_id = cursor.lastrowid

        
    print("Adding subjects...")
    exam_date_1 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    cursor.execute(
        "INSERT INTO subjects (user_id, subject_name, exam_date, difficulty) VALUES (?, ?, ?, ?)",
        (user_id, "Mathematics", exam_date_1, 5)
    )
    math_id = cursor.lastrowid
    
    exam_date_2 = (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d')
    cursor.execute(
        "INSERT INTO subjects (user_id, subject_name, exam_date, difficulty) VALUES (?, ?, ?, ?)",
        (user_id, "Physics", exam_date_2, 4)
    )
    physics_id = cursor.lastrowid

    exam_date_3 = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
    cursor.execute(
        "INSERT INTO subjects (user_id, subject_name, exam_date, difficulty) VALUES (?, ?, ?, ?)",
        (user_id, "Computer Science", exam_date_3, 3)
    )
    cs_id = cursor.lastrowid

    print("Adding tasks...")
    # Math Tasks
    math_tasks = ["Algebra Revise", "Calculus Integration", "Probability Problems", "Geometry Proofs"]
    for task in math_tasks:
        cursor.execute("INSERT INTO tasks (subject_id, topic_name, status) VALUES (?, ?, ?)", (math_id, task, 'Pending'))

    # Physics Tasks
    physics_tasks = ["Kinematics", "Thermodynamics", "Electromagnetism"]
    for task in physics_tasks:
        cursor.execute("INSERT INTO tasks (subject_id, topic_name, status) VALUES (?, ?, ?)", (physics_id, task, 'Pending'))

    # CS Tasks
    cs_tasks = ["Data Structures", "Algorithms", "Database Systems"]
    for task in cs_tasks:
        cursor.execute("INSERT INTO tasks (subject_id, topic_name, status) VALUES (?, ?, ?)", (cs_id, task, 'Pending'))

    # Also make one task completed to test progress
    cursor.execute("UPDATE tasks SET status = 'Completed' WHERE subject_id = ? AND topic_name = ?", (math_id, 'Algebra Revise'))

    conn.commit()
    conn.close()
    print("Database seeded successfully with test subjects and tasks.")

if __name__ == '__main__':
    seed_database()
