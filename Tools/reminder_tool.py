from Memory import reminder_manager

def set_reminder(message: str, minutes_from_now: int) -> str:
    r = reminder_manager.add_reminder(message, minutes_from_now)
    return f"Recordatorio #{r['id']} programado para {r['due_at']}: {message}"

def list_reminders() -> str:
    pending = reminder_manager.list_pending_reminders()
    if not pending:
        return "No hay recordatorios pendientes."
    return "\n".join(f"#{r['id']} - {r['due_at']} - {r['message']}" for r in pending)

def cancel_reminder(identifier: int) -> str:
    ok = reminder_manager.cancel_reminder(identifier)
    return f"Recordatorio #{identifier} cancelado." if ok else f"No encontré el recordatorio #{identifier}."
