import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "alex.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversation_turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_turns_channel_id ON conversation_turns(channel, id);

CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL UNIQUE,
    category TEXT,
    importance INTEGER NOT NULL DEFAULT 3,
    created_at TEXT NOT NULL,
    last_accessed_at TEXT,
    access_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_facts_importance ON facts(importance);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    due_at TEXT NOT NULL,
    channel TEXT NOT NULL DEFAULT 'telegram',
    chat_id TEXT,
    created_at TEXT NOT NULL,
    sent INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(due_at, sent);

CREATE TABLE IF NOT EXISTS kv_state (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS approved_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER UNIQUE,
    username TEXT,
    first_contact_date TEXT NOT NULL,
    alex_decision TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_approved_users_id ON approved_users(telegram_user_id);
"""

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)

def get_state(key: str) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM kv_state WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

def set_state(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO kv_state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        conn.commit()

def get_user_status(user_id: int) -> Optional[dict]:
    """Obtiene estado de aprobación de usuario. Retorna None si no existe."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM approved_users WHERE telegram_user_id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

def set_user_approved(user_id: int, username: str, reason: str = "") -> None:
    """Aprueba a un usuario."""
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO approved_users
               (telegram_user_id, username, first_contact_date, alex_decision, reason, created_at)
               VALUES (?, ?, ?, 'approved', ?, ?)
               ON CONFLICT(telegram_user_id) DO UPDATE SET
               alex_decision='approved', reason=excluded.reason, created_at=excluded.created_at""",
            (user_id, username, now, reason, now)
        )
        conn.commit()

def set_user_rejected(user_id: int, username: str, reason: str = "") -> None:
    """Rechaza a un usuario."""
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO approved_users
               (telegram_user_id, username, first_contact_date, alex_decision, reason, created_at)
               VALUES (?, ?, ?, 'rejected', ?, ?)
               ON CONFLICT(telegram_user_id) DO UPDATE SET
               alex_decision='rejected', reason=excluded.reason, created_at=excluded.created_at""",
            (user_id, username, now, reason, now)
        )
        conn.commit()
