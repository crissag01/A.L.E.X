from . import db as _db
_db.init_db()

from . import migrate as _migrate
_migrate.run_once()

from .memory_manager import (
    load_memories,
    save_memory,
    search_memories,
    get_context_for_message,
    forget,
    save_turn,
    load_history,
)