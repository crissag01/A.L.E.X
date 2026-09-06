# Mejoras de Alex - Sistema de Memoria + Herramientas

## Cambios principales implementados

### 1. **Persistencia de conversación (SQLite)**
- El historial de cada canal (Telegram, WebUI, CLI) ahora se guarda en `Memory/alex.db`
- Cuando reinicies `Telegram_bridge.py` o relances `server.py`, Alex recupera los últimos 20 turnos de conversación
- Cada turno se persiste **inmediatamente** después de ejecutarse (no hay riesgo de pérdida por crash)

### 2. **Memoria de largo plazo mejorada**
- `Memory/memory.json` fue migrada a SQLite (`facts` table) — idempotente, seguro de repetir
- Búsqueda ahora usa **TF-IDF** (no solo palabras clave) + importancia + recencia
  - Importancia (1-5): puedes darle más peso a ciertos hechos
  - Recencia: hechos antiguos se puntúan más bajo (escala ~1 año)
  - Stopwords en español para evitar ruido
- **Nueva herramienta `forget`**: ahora puedes borrar memorias (por id, texto exacto o coincidencia aproximada)

### 3. **Recordatorios proactivos (Telegram)**
```python
set_reminder(message="Revisar el portafolio", minutes_from_now=60)
```
- Alex te manda un mensaje automático por Telegram cuando se cumple la hora
- Funciona aunque reinicies el proceso (la hora se persiste en BD)
- Comando `list_reminders` para ver los pendientes, `cancel_reminder(id)` para cancelar

### 4. **Nuevas herramientas (16 total, antes 6)**

#### Ejecución
- **`execute_command(command)`** — corre cualquier comando CLI (sin whitelist, sin confirmación)
  - Ej: `execute_command("dir C:\\")`
  - Captura stdout/stderr/exit code, timeout 30s

#### Archivos
- **`write_file(path, content, mode)`** — escribe/agrega a archivo (UTF-8)
- **`delete_file(path)`** — elimina un archivo
- **`read_file(path)`** (existente, mejorada)
- **`list_directory(path)`** (existente, mejorada)

#### Sistema
- **`get_system_info()`** — CPU%, RAM (usado/total), Disco C (usado/total)
- **`open_program(program)`** — ahora sin whitelist (antes solo notepad/calc/explorer)
  - Acepta rutas, shortcuts, nombres si están en PATH

#### Información
- **`get_weather(city)`** — clima actual vía wttr.in (sin API key)
  - Ej: `get_weather("Mexico City")`
- **`web_search(query)`** — scraping HTML de DuckDuckGo (mejor que antes)
- **`calculate(expression)`** — eval seguro de matemáticas (no "eval" crudo)
  - Ej: `calculate("2**3 + 10/5")`

#### Memoria
- **`remember(text)`** (existente, ahora en SQLite)
- **`forget(identifier)`** (nueva)
  - Ej: `forget("algunas memorias falsas")` o `forget(5)` (por id)

#### Recordatorios
- **`set_reminder(message, minutes_from_now)`** (nueva)
- **`list_reminders()`** (nueva) — lista pendientes
- **`cancel_reminder(id)`** (nueva) — cancela uno

#### Tiempo
- **`get_time()`** (existente)

### 5. **Historial por canal**
- `server.py` → canal `"web"` (WebUI React)
- `Telegram_bridge.py` → canal `"telegram"`
- `Alex.py` → canal `"cli"` (scripts/testing no contaminan el hilo real)
- Cada canal tiene su propio historial persistente, independiente

### 6. **Fixes incidentales**
- `server.py`: `/resources` ahora reporta `"model": "claude-haiku-4-5-20251001"` en lugar del stale `"qwen:7b"`
- `server.py`: `load_chats()` y `save_chats()` ahora usan `encoding="utf-8"` (evita mojibake en `chats.json`)

## Archivos nuevos

```
Memory/db.py              ← schema SQLite + conexión (WAL mode para concurrencia)
Memory/migrate.py         ← migración idempotente de memory.json → sqlite
Memory/reminder_manager.py ← gestión de recordatorios
Tools/shell_tool.py       ← execute_command
Tools/reminder_tool.py    ← set_reminder, list_reminders, cancel_reminder
Tools/weather_tool.py     ← get_weather
Tools/calc_tool.py        ← calculate (AST whitelist, no eval crudo)
test_system.py            ← test rápido de carga (opcional, puedes eliminar)
test_persistence.py       ← inspección de BD (opcional)
```

## Archivos modificados

```
Memory/__init__.py        ← inicia DB + migración automáticamente
Memory/memory_manager.py  ← reescritura completa (SQLite backend)
Brain/brain.py            ← per-channel history, TOOLS_SCHEMA, save_turn
Tools/tool_manager.py     ← registra 16 herramientas
Tools/files.py            ← + write_file, delete_file
Tools/memory_tool.py      ← + forget
Tools/system_tool.py      ← open_program sin whitelist + get_system_info
Tools/web_search.py       ← scraping DuckDuckGo HTML (mejor cobertura)
Telegram_bridge.py        ← channel="telegram", check_reminders()
Alex.py                   ← channel="cli"
server.py                 ← channel="web", encoding fixes, model string fix
```

## Cómo usar

### Memoria
```python
# Guardar
"Recuerda que mi jefe es Roberto"

# Buscar automáticamente (en cada pregunta)
# Alex busca memorias relevantes sin que lo pidas

# Borrar
"Olvida que mi jefe es Roberto"
# o
forget(5)  # por id
```

### Recordatorios
```python
# Programar
"Recuérdame en 30 minutos que debo revisar el código"

# Ver pendientes
list_reminders()

# Cancelar
cancel_reminder(3)  # por id
```

### Ejecución de comandos
```python
# Windows
execute_command("dir C:\\Users")
execute_command("python --version")
execute_command("git status")

# Captura stdout/stderr/exit code automáticamente
```

### Archivos
```python
# Escribir
write_file("C:\\temp\\nota.txt", "contenido", mode="overwrite")

# Agregar
write_file("C:\\temp\\nota.txt", "\nlinea nueva", mode="append")

# Leer
read_file("C:\\temp\\nota.txt")

# Listar directorio
list_directory("C:\\Users\\criss\\Downloads")

# Eliminar
delete_file("C:\\temp\\temporal.txt")
```

### Sistema
```python
# Info del sistema
get_system_info()
# → "CPU: 25%\nRAM: 8.3 / 16.0 GB (51%)\nDisco C: 450.2 / 931.5 GB (48%)"

# Abrir programa
open_program("C:\\Program Files\\Google\\Chrome\\chrome.exe")
open_program("notepad")  # si está en PATH
open_program("explorer")
```

### Clima
```python
get_weather("Mexico City")
# → "Mexico City 22°C 🌤"
```

### Búsqueda
```python
web_search("python async await")
# → lista los 5 primeros resultados de DuckDuckGo
```

### Cálculo
```python
calculate("2**3 + 10/5")
# → "2**3 + 10/5 = 10.0"
```

## Arquitectura SQLite

```sql
-- Historial de conversación (por canal)
CREATE TABLE conversation_turns (
    id INTEGER PRIMARY KEY,
    channel TEXT,           -- "web", "telegram", "cli"
    role TEXT,              -- "user" o "assistant"
    content TEXT,           -- JSON serializado (puede tener tool_use, etc)
    created_at TEXT
);

-- Hechos / memoria a largo plazo
CREATE TABLE facts (
    id INTEGER PRIMARY KEY,
    text TEXT UNIQUE,       -- el hecho en sí
    category TEXT,          -- "perfil", "proyecto", etc (nullable)
    importance INTEGER,     -- 1-5 (default 3), afecta búsqueda
    created_at TEXT,
    last_accessed_at TEXT,  -- se actualiza cuando se busca/accede
    access_count INTEGER    -- cuántas veces fue encontrada
);

-- Recordatorios futuros
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY,
    message TEXT,
    due_at TEXT,            -- ISO datetime
    channel TEXT DEFAULT 'telegram',
    chat_id TEXT,           -- resolverse en tiempo de envío (vía kv_state)
    created_at TEXT,
    sent INTEGER DEFAULT 0  -- 1 si fue enviado
);

-- Key-value state (flags, config, último chat_id conocido)
CREATE TABLE kv_state (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

## Comandos Telegram (NUEVO)

Ahora puedes enviar comandos a Alex por Telegram sin que ella procese como conversación:

```
/help              - Ver todos los comandos disponibles
/stats             - Estadísticas (turnos, memorias, recordatorios)
/compact           - Compactar base de datos SQLite
/clear_history     - Borrar historial de Telegram
/list_reminders    - Ver recordatorios pendientes
/memory            - Ver últimas 10 memorias guardadas
/exec <comando>    - Ejecutar comando CLI directamente (sin pasar por Alex)
/forget_all        - Borrar TODAS las memorias (irreversible)
/status            - Estado completo del sistema
```

**Ejemplos:**
```
/exec dir C:\Users\criss\Downloads
/exec python --version
/exec git status
```

## Autonomía de Alex (MEJORADO)

- Alex ahora **toma decisiones sin esperar permiso**
- Si ve algo que debería guardarse, lo guarda automáticamente
- Si encuentra una solución, la ejecuta sin pedir aprobación
- Usa herramientas de forma más proactiva y natural en conversación

## Visión: Imágenes y archivos (NUEVO)

- **Imágenes en Telegram**: Alex ahora puede ver imágenes que le envíes
  - Automáticamente descargadas desde Telegram
  - Convertidas a base64 y enviadas a Claude
  - Soporta: JPEG, PNG, GIF, WebP
  
- **Archivos de texto**: Alex puede leer documentos
  - `.txt`, `.md` se extraen automáticamente
  - Convertidos en contexto para el análisis
  
**Ejemplo:**
```
Enviar foto + mensaje "¿Qué ves aquí?"
→ Alex analiza la imagen y responde
```

## Streaming en tiempo real (NUEVO)

- La animación "escribiendo" en Telegram es **en vivo**
- El mensaje se **actualiza mientras Alex escribe**
- Sin esperar a que termine para mostrar contenido
- Más rápido de ver respuestas parciales

**Técnicamente:**
- Usa `messages.stream()` de Claude API (chunked responses)
- Edita el mensaje cada 3 chunks (economiza API)
- Soporta Markdown en las respuestas

## Mensajes estructurados (MEJORADO)

- Las respuestas ahora usan **Markdown**
- Párrafos claros y concisos
- Listas con viñetas (`•`), flechas (`->`), opciones (`-`)
- **Negrita** para lo importante, `` `código` `` para técnico
- Encabezados (`##`) para secciones grandes

## Próximas mejoras posibles (fuera de scope actual)

1. **Búsqueda mejorada**: integrar una API real (Brave Search, Tavily) en lugar de scraping
2. **Embeddings**: si `CLAUDE.md` se relaja, usar ChromaDB o similar para búsqueda semántica
3. **Historial en WebUI**: mostrar en la interfaz React que se puede hacer rollback a conversaciones pasadas
4. **Editor de memorias**: UI para ver/editar/borrar facts con importancia
5. **Recordatorios con repetición**: "cada lunes", "cada 15 días", etc.
6. **Backup automático**: snapshot semanal de `Memory/alex.db`
7. **Exportar historial**: generar un PDF o markdown de una conversación completa
8. **Notificaciones push**: alertas de recordatorios en Windows (además de Telegram)

## Ejecución integrada

Ahora **solo necesitas un proceso**:

```bash
# Terminal 1: Backend + Telegram Bridge integrados
python server.py

# Terminal 2: Frontend React (opcional, para WebUI)
npm run dev
```

**Nota:** `Telegram_bridge.py` sigue siendo un script independiente opcional si prefieres ejecutar el polling de Telegram en un proceso separado. Pero `server.py` ya lo incluye como tarea de background.

## Testing

```bash
# Test rápido de sistema
python test_system.py

# Inspeccionar BD
sqlite3 Memory/alex.db
> SELECT COUNT(*) FROM facts;
> SELECT role, substr(content, 1, 80) FROM conversation_turns LIMIT 5;

# Limpiar una conversación de testing
sqlite3 Memory/alex.db
> DELETE FROM conversation_turns WHERE channel = 'test';
```

## Rollback (si algo sale mal)

1. `Memory/memory.json.bak` — backup manual del estado anterior (guárdalo)
2. Deletea `Memory/alex.db` si quieres empezar limpio
3. Al importar `Memory`, la migración se ejecuta de nuevo automáticamente

## Seguridad/riesgos notables

- **`execute_command` sin restricciones**: puede ejecutar CUALQUIER comando (elegiste esto explícitamente). Ten cuidado con lo que pides a Alex.
- **`open_program` sin whitelist**: similar, ahora puede abrir cualquier ejecutable.
- **Web scraping**: `web_search` depende de markup de DuckDuckGo — si cambian, se rompe (pero es mejor que antes).
- **`wttr.in` sin SLA**: servicio gratuito, puede tener downtime o rate-limiting.

---

**Fecha**: 2026-07-03
**Estado**: Implementación completa + Haiku 4.5 + Vision + Streaming
**Modelo**: claude-haiku-4-5-20251001 (rápido, costo bajo)
**Extended Thinking**: Deshabilitado para Haiku (no es compatible)
