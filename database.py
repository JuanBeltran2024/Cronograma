import sqlite3
import os

DB_FILENAME = "tasks.db"

def get_connection():
    # If using PyInstaller onefile, the working directory might be temp
    # Let's ensure the DB is created in the user's APPDATA or the same dir as the exe.
    # For simplicity, during dev, we'll keep it in the current directory.
    # We can detect APPDATA later. For now, let's keep it next to the script.
    return sqlite3.connect(DB_FILENAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            session_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    ''')
    try:
        cursor.execute('ALTER TABLE tasks ADD COLUMN importance INTEGER DEFAULT 1')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def add_task(title, description, due_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, description, due_date, status)
        VALUES (?, ?, ?, 'pending')
    ''', (title, description, due_date))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Sort purely by due_date now. We will calculate importance in UI based on proximity to today.
    cursor.execute('SELECT * FROM tasks ORDER BY due_date ASC')
    tasks = cursor.fetchall()
    conn.close()
    return [dict(row) for row in tasks]

def get_tasks_by_date_range(start_date, end_date):
    # Depending on date format (YYYY-MM-DD recommended)
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tasks 
        WHERE due_date >= ? AND due_date <= ?
        ORDER BY due_date ASC
    ''', (start_date, end_date))
    tasks = cursor.fetchall()
    conn.close()
    return [dict(row) for row in tasks]

def update_task_status(task_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
    
    # Update 7: If task is completed, remove all its scheduled time blocks automatically.
    if new_status == 'completed':
        cursor.execute('DELETE FROM sessions WHERE task_id = ?', (task_id,))
        
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    # Enable foreign keys so CASCADE works
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def add_session(task_id, session_date, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (task_id, session_date, start_time, end_time)
        VALUES (?, ?, ?, ?)
    ''', (task_id, session_date, start_time, end_time))
    conn.commit()
    conn.close()

def get_sessions_by_date_range(start_date, end_date):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id as session_id, s.session_date, s.start_time, s.end_time,
               t.id as task_id, t.title, t.status 
        FROM sessions s
        JOIN tasks t ON s.task_id = t.id
        WHERE s.session_date >= ? AND s.session_date <= ?
        ORDER BY s.session_date ASC, s.start_time ASC
    ''', (start_date, end_date))
    sessions = cursor.fetchall()
    conn.close()
    return [dict(row) for row in sessions]

def delete_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()

def add_class(name, day_of_week, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO classes (name, day_of_week, start_time, end_time)
        VALUES (?, ?, ?, ?)
    ''', (name, day_of_week, start_time, end_time))
    conn.commit()
    conn.close()

def get_all_classes():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM classes ORDER BY day_of_week ASC, start_time ASC')
    classes = cursor.fetchall()
    conn.close()
    return [dict(row) for row in classes]

def delete_class(class_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM classes WHERE id = ?', (class_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
