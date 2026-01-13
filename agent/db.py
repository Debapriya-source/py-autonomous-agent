"""SQLite database operations."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

AGENT_DIR = ".agent"
DB_NAME = "agent.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    name TEXT,
    initialized_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    key TEXT NOT NULL,
    value TEXT,
    category TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, key)
);

CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    title TEXT,
    description TEXT,
    source_file TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    plan_id INTEGER REFERENCES plans(id),
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    parent_task_id INTEGER REFERENCES tasks(id),
    result TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    agent_type TEXT,
    input TEXT,
    output TEXT,
    success INTEGER,
    executed_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def get_agent_dir(project_path: Path = None) -> Path:
    """Get .agent directory path."""
    base = project_path or Path.cwd()
    return base / AGENT_DIR

def get_db_path(project_path: Path = None) -> Path:
    """Get database path."""
    return get_agent_dir(project_path) / DB_NAME

def ensure_agent_dir(project_path: Path = None) -> Path:
    """Create .agent dir if not exists."""
    agent_dir = get_agent_dir(project_path)
    agent_dir.mkdir(exist_ok=True)
    (agent_dir / "plans").mkdir(exist_ok=True)
    return agent_dir

@contextmanager
def get_db(project_path: Path = None):
    """Get database connection."""
    db_path = get_db_path(project_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(project_path: Path = None):
    """Initialize database schema."""
    ensure_agent_dir(project_path)
    with get_db(project_path) as conn:
        conn.executescript(SCHEMA)

# Project ops
def get_or_create_project(path: Path = None) -> int:
    """Get or create project record."""
    path = path or Path.cwd()
    with get_db(path) as conn:
        row = conn.execute("SELECT id FROM projects WHERE path = ?", (str(path),)).fetchone()
        if row:
            return row["id"]
        cur = conn.execute("INSERT INTO projects (path, name) VALUES (?, ?)",
                          (str(path), path.name))
        return cur.lastrowid

# Knowledge ops
def set_knowledge(key: str, value: str, category: str = "general", project_path: Path = None):
    """Store knowledge."""
    proj_id = get_or_create_project(project_path)
    with get_db(project_path) as conn:
        conn.execute("""
            INSERT INTO knowledge (project_id, key, value, category, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_id, key) DO UPDATE SET value=?, category=?, updated_at=?
        """, (proj_id, key, value, category, datetime.now().isoformat(),
              value, category, datetime.now().isoformat()))

def get_knowledge(key: str = None, category: str = None, project_path: Path = None) -> list:
    """Get knowledge entries."""
    proj_id = get_or_create_project(project_path)
    with get_db(project_path) as conn:
        if key:
            row = conn.execute("SELECT * FROM knowledge WHERE project_id=? AND key=?",
                              (proj_id, key)).fetchone()
            return dict(row) if row else None
        elif category:
            rows = conn.execute("SELECT * FROM knowledge WHERE project_id=? AND category=?",
                               (proj_id, category)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM knowledge WHERE project_id=?",
                               (proj_id,)).fetchall()
        return [dict(r) for r in rows]

# Plan ops
def create_plan(title: str, description: str, source_file: str = None, project_path: Path = None) -> int:
    """Create a plan."""
    proj_id = get_or_create_project(project_path)
    with get_db(project_path) as conn:
        cur = conn.execute("""
            INSERT INTO plans (project_id, title, description, source_file)
            VALUES (?, ?, ?, ?)
        """, (proj_id, title, description, source_file))
        return cur.lastrowid

def get_plans(status: str = None, project_path: Path = None) -> list:
    """Get plans."""
    proj_id = get_or_create_project(project_path)
    with get_db(project_path) as conn:
        if status:
            rows = conn.execute("SELECT * FROM plans WHERE project_id=? AND status=?",
                               (proj_id, status)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM plans WHERE project_id=?",
                               (proj_id,)).fetchall()
        return [dict(r) for r in rows]

def update_plan_status(plan_id: int, status: str, project_path: Path = None):
    """Update plan status."""
    with get_db(project_path) as conn:
        conn.execute("UPDATE plans SET status=? WHERE id=?", (status, plan_id))

# Task ops
def create_task(plan_id: int, title: str, description: str = "", task_type: str = "code",
                priority: int = 0, parent_id: int = None, project_path: Path = None) -> int:
    """Create a task."""
    with get_db(project_path) as conn:
        cur = conn.execute("""
            INSERT INTO tasks (plan_id, title, description, task_type, priority, parent_task_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (plan_id, title, description, task_type, priority, parent_id))
        return cur.lastrowid

def get_tasks(plan_id: int = None, status: str = None, project_path: Path = None) -> list:
    """Get tasks."""
    with get_db(project_path) as conn:
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if plan_id:
            query += " AND plan_id=?"
            params.append(plan_id)
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY priority DESC, id ASC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

def update_task(task_id: int, status: str = None, result: str = None, project_path: Path = None):
    """Update task."""
    with get_db(project_path) as conn:
        if status:
            conn.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
            if status == "completed":
                conn.execute("UPDATE tasks SET completed_at=? WHERE id=?",
                            (datetime.now().isoformat(), task_id))
        if result:
            conn.execute("UPDATE tasks SET result=? WHERE id=?", (result, task_id))

def get_next_task(project_path: Path = None) -> dict:
    """Get next pending task."""
    tasks = get_tasks(status="pending", project_path=project_path)
    return tasks[0] if tasks else None

# Execution ops
def log_execution(task_id: int, agent_type: str, input_data: str, output: str,
                  success: bool, project_path: Path = None) -> int:
    """Log execution."""
    with get_db(project_path) as conn:
        cur = conn.execute("""
            INSERT INTO executions (task_id, agent_type, input, output, success)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, agent_type, input_data, output, int(success)))
        return cur.lastrowid

# Reset
def reset_tasks(project_path: Path = None):
    """Clear all tasks and plans."""
    with get_db(project_path) as conn:
        conn.execute("DELETE FROM executions")
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM plans")
