from Memory.memory_manager import save_memory, forget as _forget

def remember(text):
    """Guarda una memoria."""
    result = save_memory(text)
    if result:
        return f"Memoria guardada: {text}"
    else:
        return "Memoria ya existia."

def forget(identifier):
    """Elimina una memoria por id o por texto (exacto o aproximado)."""
    return _forget(identifier)