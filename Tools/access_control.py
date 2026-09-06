"""Control de acceso: Alex decide quién puede contactarla"""
import os
from dotenv import load_dotenv
from Memory.db import get_user_status, set_user_approved, set_user_rejected

load_dotenv()
OWNER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))


def is_owner(user_id: int) -> bool:
    """¿Es el dueño (Cris)?"""
    return user_id == OWNER_ID


def check_access(user_id: int) -> tuple[bool, str]:
    """
    Verifica si un usuario tiene acceso.

    Retorna: (allowed: bool, status: str)
    - (True, "owner") → Es Cris
    - (True, "approved") → Fue aprobado por Alex
    - (False, "rejected") → Alex lo rechazó
    - (False, "new") → Primera vez, Alex debe decidir
    """
    if is_owner(user_id):
        return True, "owner"

    user = get_user_status(user_id)
    if not user:
        return False, "new"

    if user["alex_decision"] == "approved":
        return True, "approved"
    else:
        return False, "rejected"


def needs_alex_decision(user_id: int) -> bool:
    """¿Es un usuario nuevo que necesita aprobación de Alex?"""
    allowed, status = check_access(user_id)
    return status == "new"


def approve_user(user_id: int, username: str, reason: str = "") -> None:
    """Alex aprobó este usuario"""
    set_user_approved(user_id, username, reason)


def reject_user(user_id: int, username: str, reason: str = "") -> None:
    """Alex rechazó este usuario"""
    set_user_rejected(user_id, username, reason)


def get_access_decision_prompt(user_id: int, username: str, message: str) -> str:
    """
    Genera un prompt para que Alex decida sobre un nuevo usuario.
    Se inserta en el contexto del mensaje.
    """
    return f"""
⚠️ SOLICITUD DE ACCESO

Usuario nuevo intenta contactarte:
- ID: {user_id}
- Username: {username}
- Mensaje: "{message}"

DECIDE TÚ:
- Si respondes normalmente o "aprobado" → se guarda como APPROVED
- Si responder "rechazado" o "acceso denegado" → se guarda como REJECTED
- Si ignoras (sin responder) → se trata como REJECTED

Esto es TU DECISIÓN. Analiza si es una amenaza o alguien legítimo.
---
"""
