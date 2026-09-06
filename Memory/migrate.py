import json
import os
from datetime import datetime
from Memory import db

LEGACY_JSON_PATH = os.path.join(os.path.dirname(__file__), "memory.json")
MIGRATION_FLAG = "migrated_json_to_sqlite_v1"

def run_once() -> None:
    db.init_db()
    if db.get_state(MIGRATION_FLAG):
        return
    _migrate()
    db.set_state(MIGRATION_FLAG, "1")

def _migrate() -> None:
    data = _load_legacy_json()
    now = datetime.now().isoformat()
    with db.get_connection() as conn:
        for text in data.get("memories", []):
            text = (text or "").strip()
            if text:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO facts (text, category, importance, created_at, access_count) "
                        "VALUES (?, NULL, 3, ?, 0)",
                        (text, now)
                    )
                except sqlite3.IntegrityError:
                    pass

        user = data.get("user") or {}
        if user:
            sentence = "Datos del usuario: " + ", ".join(
                f"{k} = {v}" for k, v in user.items()
            ) + "."
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO facts (text, category, importance, created_at, access_count) "
                    "VALUES (?, 'perfil', 5, ?, 0)",
                    (sentence, now)
                )
            except sqlite3.IntegrityError:
                pass

        project = data.get("project") or {}
        if project:
            sentence = "Datos del proyecto: " + ", ".join(
                f"{k} = {v}" for k, v in project.items()
            ) + "."
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO facts (text, category, importance, created_at, access_count) "
                    "VALUES (?, 'proyecto', 2, ?, 0)",
                    (sentence, now)
                )
            except sqlite3.IntegrityError:
                pass

        conn.commit()

def _load_legacy_json() -> dict:
    try:
        with open(LEGACY_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

if __name__ == "__main__":
    run_once()
    print("Migración completada (o ya estaba hecha).")
