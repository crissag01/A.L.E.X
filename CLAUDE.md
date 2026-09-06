# Alex - Instrucciones de trabajo

## Contexto del proyecto

Alex es un **agente personal singular** (no multiagente) enfocado 100% en Cris. Basado en la personalidad de Alex Brand de Gears of War: directo, escéptico, cínico, detecta amenazas.

## Stack actual

- **Backend**: Python + FastAPI + Claude Sonnet 4.6
- **Frontend**: React 18 + TypeScript + Vite
- **Memoria**: SQLite con TF-IDF search (sin embeddings)
- **Control de acceso**: Alex decide quién puede contactarla (Pairing avanzado)
- **Herramientas**: 16 tools (time, remember, forget, execute_command, write_file, delete_file, set_reminder, list_reminders, cancel_reminder, get_weather, get_system_info, calculate, open_program, list_directory, web_search, read_file)

## Cómo proceder

### Antes de hacer cambios

1. **Lee ALEX_AGENT.md** para entender la arquitectura
2. **Nunca hagas multiagentes** - Alex es singular
3. **Mantén la personalidad** - Directo, cínico, detecta amenazas

### Si reportas bugs

```
[Problema]
[Dónde sucede]
[Pasos para reproducir]
[Comportamiento esperado vs actual]
```

### Si pides features

```
[Qué quieres lograr]
[Por qué lo necesitas]
[Cómo debería verse/funcionar]
```

## Reglas de oro

✓ Extended thinking siempre activado (cost es bajo comparado con el valor)
✓ Herramientas autónomas (Alex decide cuándo usarlas)
✓ Memoria integrada en cada razonamiento
✓ Una sola entidad (Alex), no coordinador
✓ Personalidad consistente en todas las respuestas

## Archivos clave

- `Brain/brain.py` - Lógica del agente
- `Memory/memory_manager.py` - Sistema de memoria
- `src/AlexDashboard.tsx` - Frontend
- `server.py` - API FastAPI
- `Tools/tool_manager.py` - Definición de herramientas

## Testing

```bash
# Test de control de acceso
python test_access_control.py

# Prueba rápida de memoria
python test_memory_simple.py

# Prueba completa de Alex (CLI)
python Alex.py

# Frontend dev
npm run dev

# Backend + Telegram integrado
python server.py
```

## Ejecutar todo

**Un solo servicio** (backend FastAPI + Telegram Bridge + WebUI, un solo puerto):
```bash
npm run build              # solo si cambiaste src/AlexDashboard.tsx
.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000
```

Luego accede a http://localhost:8000 (WebUI servida por el propio backend) o envía mensajes por Telegram al bot.

**Nota:** `python server.py` NO arranca nada — `server.py` no tiene bloque `if __name__ == "__main__"`, solo define la app. Siempre se arranca vía `uvicorn server:app`.

**Modo desarrollo del dashboard** (hot-reload, dos procesos separados en vez de uno):
```bash
# Terminal 1
.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000
# Terminal 2
npm run dev   # http://localhost:5173, pega directo a la API en :8000
```
Cuando termines de iterar en `src/AlexDashboard.tsx`, corre `npm run build` para que el servicio único (puerto 8000) sirva la versión actualizada.

**Nota:** Telegram Bridge está integrado en `server.py` como tarea de background del propio proceso de uvicorn. No necesitas ejecutar `Telegram_bridge.py` por separado, pero sigue siendo disponible como script independiente si lo necesitas.

## Notas técnicas

- Python 3.14.6 (compatible)
- Anthropic SDK (versión reciente)
- No usar ChromaDB (incompatible con Python 3.14)
- Modelo: Claude Sonnet 4.6 (mejor calidad, mayor razonamiento)
- Extended Thinking: Activado en todas las llamadas

## Próximas mejoras sugeridas

1. **Multicanal avanzado** - Discord, Slack, WhatsApp (como OpenClaw)
2. **Navegador integrado** - Navegar webs reales con screenshot
3. **Plugin system** - Skills dinámicas cargables
4. **Multi-modelo** - Fallback a GPT-4 o Gemini si Haiku falla
5. **Logging mejorado** - Rastrear decisiones y auditoria

---

**Última actualización:** 2026-07-04
**Estado**: Agentic + Sonnet 4.6 + SQLite + Vision + Streaming + Spanish MX + Access Control
**Control de acceso**: Alex decide quién puede contactarla (Pairing)
**Género**: Mujer
**Personalidad**: Frí­a, directa, seca, sarcástica, cínica
**Idioma**: Español mexicano neutro
**Rol**: Asistente personal singular de Cris (100% enfocada en él)
