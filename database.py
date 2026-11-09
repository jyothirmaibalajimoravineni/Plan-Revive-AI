import sqlite3
import hashlib
import secrets

DB_NAME = "planrevive.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            description TEXT,
            deadline INTEGER NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            dependencies TEXT DEFAULT '',
            assigned_member TEXT DEFAULT '',
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disruptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            disruption_type TEXT NOT NULL,
            affected_task TEXT NOT NULL,
            delay_days INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recovery_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            strategy_name TEXT NOT NULL,
            completion_days INTEGER NOT NULL,
            feasibility TEXT NOT NULL,
            is_selected INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()


def register_user(username, password):
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    conn.close()

    if user is None:
        return None

    entered_hash = hash_password(password, user["salt"])

    if secrets.compare_digest(entered_hash, user["password_hash"]):
        return user["id"]

    return None


def create_project(user_id, project_name, description, deadline):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        existing_project = conn.execute(
            """
            SELECT 1
            FROM projects
            WHERE user_id = ?
              AND lower(trim(project_name)) = lower(trim(?))
            LIMIT 1
            """,
            (user_id, project_name)
        ).fetchone()

        if existing_project:
            raise ValueError(
                "A project with this name already exists. "
                "Choose a different name."
            )

        cursor = conn.execute(
            """INSERT INTO projects
               (user_id, project_name, description, deadline)
               VALUES (?, ?, ?, ?)""",
            (user_id, project_name.strip(), description, deadline)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def project_name_exists(user_id, project_name):
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT 1
            FROM projects
            WHERE user_id = ?
              AND lower(trim(project_name)) = lower(trim(?))
            LIMIT 1
            """,
            (user_id, project_name)
        ).fetchone() is not None
    finally:
        conn.close()


def add_task(project_id, task_name, duration,
             dependencies="", assigned_member=""):

    conn = get_connection()

    conn.execute(
        """INSERT INTO tasks
           (project_id, task_name, duration, dependencies, assigned_member)
           VALUES (?, ?, ?, ?, ?)""",
        (project_id, task_name, duration, dependencies, assigned_member)
    )

    conn.commit()
    conn.close()


def get_user_projects(user_id):
    conn = get_connection()

    projects = conn.execute(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

    conn.close()
    return projects


def get_project_tasks(project_id):
    conn = get_connection()

    tasks = conn.execute(
        "SELECT * FROM tasks WHERE project_id = ?",
        (project_id,)
    ).fetchall()

    conn.close()
    return tasks


def update_task_status(task_id, status):
    conn = get_connection()

    conn.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (status, task_id)
    )

    conn.commit()
    conn.close()
