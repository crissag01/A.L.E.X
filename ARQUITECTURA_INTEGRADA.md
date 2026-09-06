# Arquitectura integrada: Un solo proceso

## Antes (2 procesos)

```
┌─────────────────────────────────────────────────┐
│ Terminal 1: python server.py                    │
│  ├─ FastAPI (puerto 8000)                       │
│  ├─ Chat WebUI (canal "web")                    │
│  └─ /chat, /resources, /chats endpoints         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Terminal 2: python Telegram_bridge.py           │
│  ├─ Polling de Telegram (long-poll 30s)         │
│  ├─ Procesa mensajes (canal "telegram")         │
│  └─ Verifica recordatorios cada ciclo           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Terminal 3: npm run dev                         │
│  └─ React dev server (puerto 5173)              │
└─────────────────────────────────────────────────┘
```

## Ahora (1 proceso principal)

```
┌──────────────────────────────────────────────────────────┐
│ Terminal 1: python server.py                             │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ FastAPI (puerto 8000)                              │  │
│  │  ├─ /chat              (WebUI messages)            │  │
│  │  ├─ /resources         (system info)               │  │
│  │  └─ /chats             (chat persistence)          │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Telegram Bridge (Background thread)                │  │
│  │  ├─ Polling async (long-poll 30s)                 │  │
│  │  ├─ Procesa mensajes (canal "telegram")           │  │
│  │  └─ Verifica recordatorios cada ciclo             │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ SQLite Database (compartida, WAL mode)             │  │
│  │  ├─ conversation_turns (historial por canal)       │  │
│  │  ├─ facts (memoria a largo plazo)                 │  │
│  │  ├─ reminders (recordatorios)                      │  │
│  │  └─ kv_state (flags, chat_id, estado)             │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ Terminal 2: npm run dev                                  │
│  └─ React dev server (puerto 5173)                       │
└──────────────────────────────────────────────────────────┘
```

## Flujo de ejecución

### Al iniciar `python server.py`

1. **Lifespan startup** (FastAPI):
   - Inicializa base de datos SQLite (`Memory/db.py`)
   - Ejecuta migración idempotente (`Memory/migrate.py`)
   - Arranca thread daemon para Telegram polling

2. **Thread de Telegram** (en background):
   - Llama a `start_telegram_polling()`
   - Infinito: `get_updates()` → `process_message()` → `ask(channel="telegram")`
   - Cada ciclo verifica recordatorios con `check_reminders()`
   - No bloquea a FastAPI (es daemon thread)

3. **FastAPI escucha en puerto 8000**:
   - POST `/chat` — mensajes WebUI (canal "web")
   - GET `/resources` — info del sistema
   - POST/GET `/chats` — persistencia de chats

## Beneficios

✅ **Un solo proceso** — simplifica deployment, less PID clutter
✅ **Mismo archivo de BD** — SQLite WAL maneja concurrencia automáticamente
✅ **Thread daemon** — muere cuando `server.py` termina, no zombie processes
✅ **Sin cambios de API** — ambos canales ("web" y "telegram") funcionan igual

## Desventajas mitigadas

- **Si FastAPI se crashea, Telegram también cae** → Pero normalmente es OK, ambos son lo mismo
- **Debugging más complejo** — pero `print()` statements van al mismo stdout
- **No se puede escalado horizontal de Telegram** — OK para uso personal

## Fallback: Telegram_bridge.py independiente

Si necesitas ejecutar Telegram en un proceso separado (debugging, load testing, etc):

```bash
python Telegram_bridge.py
```

Sigue funcionando como script independiente. Los cambios:
- Importa `handle_command` de `Tools/telegram_commands.py` (compartido)
- Usa la misma BD (SQLite WAL lo maneja)
- Polling independiente

## Módulos compartidos

- **`Tools/telegram_commands.py`** — Manejo de comandos (`/help`, `/stats`, `/exec`, etc)
  - Reutilizado por `server.py` y `Telegram_bridge.py`
  - Recibe `send_message_fn` como callback para abstracción

## Diagrama de módulos

```
server.py
├─ FastAPI lifespan startup
├─ start_telegram_polling() → threading.Thread()
│  ├─ get_updates() [loop infinito]
│  ├─ process_message()
│  │  ├─ ask(text, channel="telegram")
│  │  └─ handle_command() ← imported
│  └─ check_reminders()
├─ Memory/ (shared SQLite)
├─ Brain/brain.py
└─ Tools/telegram_commands.py ← shared

Telegram_bridge.py (optional)
├─ start_polling() [same logic]
├─ get_updates() [loop infinito]
├─ process_message()
│  ├─ ask(text, channel="telegram")
│  └─ handle_command() ← same import
└─ Tools/telegram_commands.py ← shared
```

---

**Última actualización:** 2026-07-03
**Simplificación:** Integración de Telegram Bridge en FastAPI como thread daemon
