from datetime import datetime, timedelta
from typing import List, Optional
from Memory import db

def add_reminder(message: str, minutes_from_now: int, channel: str = "telegram") -> dict:
    due_at = (datetime.now() + timedelta(minutes=minutes_from_now)).isoformat()
    now = datetime.now().isoformat()
    with db.get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO reminders (message, due_at, channel, chat_id, created_at, sent) "
            "VALUES (?, ?, ?, NULL, ?, 0)",
            (message, due_at, channel, now)
        )
        conn.commit()
        return {"id": cur.lastrowid, "due_at": due_at, "message": message}

def get_due_reminders() -> List[dict]:
    now = datetime.now().isoformat()
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT id, message, due_at FROM reminders WHERE sent = 0 AND due_at <= ? ORDER BY due_at",
            (now,)
        ).fetchall()
    return [dict(r) for r in rows]

def mark_sent(reminder_id: int) -> None:
    with db.get_connection() as conn:
        conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))
        conn.commit()

def list_pending_reminders(channel: Optional[str] = None) -> List[dict]:
    with db.get_connection() as conn:
        if channel:
            rows = conn.execute(
                "SELECT id, message, due_at FROM reminders WHERE sent = 0 AND channel = ? ORDER BY due_at",
                (channel,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, message, due_at FROM reminders WHERE sent = 0 ORDER BY due_at"
            ).fetchall()
    return [dict(r) for r in rows]

def cancel_reminder(identifier: int) -> bool:
    with db.get_connection() as conn:
        cur = conn.execute("DELETE FROM reminders WHERE id = ? AND sent = 0", (int(identifier),))
        conn.commit()
        return cur.rowcount > 0
