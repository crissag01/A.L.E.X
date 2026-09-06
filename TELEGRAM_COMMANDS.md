# Comandos Telegram para Alex

Envía estos comandos por Telegram al bot de Alex. Los comandos empiezan con `/`.

## Sistema & Información

| Comando | Descripción |
|---------|-------------|
| `/help` | Muestra este menú de comandos |
| `/status` | Estado completo del sistema (CPU, RAM, Disco, modelo, etc) |
| `/stats` | Estadísticas rápidas (turnos, memorias, recordatorios pendientes) |

## Base de datos

| Comando | Descripción |
|---------|-------------|
| `/compact` | Compacta el archivo de base de datos (PRAGMA optimize + VACUUM) |
| `/clear_history` | Borra TODO el historial de conversación en Telegram |

## Memoria

| Comando | Descripción |
|---------|-------------|
| `/memory` | Muestra las últimas 10 memorias guardadas |
| `/forget_all` | Borra TODAS las memorias (⚠️ IRREVERSIBLE) |

## Recordatorios

| Comando | Descripción |
|---------|-------------|
| `/list_reminders` | Lista todos los recordatorios pendientes |

## Ejecución directa

| Comando | Descripción |
|---------|-------------|
| `/exec <comando>` | Ejecuta un comando CLI directamente (sin pasar por Alex) |

### Ejemplos de /exec

```
/exec dir C:\
/exec python --version
/exec git status
/exec tasklist
/exec ipconfig /all
```

---

## Características adicionales

### Imágenes
- Envía fotos por Telegram
- Alex las analiza automáticamente
- Soporta: JPEG, PNG, GIF, WebP

**Ejemplo:**
```
[Envía captura de pantalla]
"¿Qué ves aquí?"
→ Alex analiza y responde
```

### Archivos de texto
- Envía `.txt`, `.md`, código, etc.
- Alex los lee y analiza automáticamente

**Ejemplo:**
```
[Envía script.py]
"¿Hay bugs?"
→ Alex extrae contenido y revisa
```

### Escritura en tiempo real
- Ves a Alex escribir mientras responde
- El mensaje se actualiza cada pocos chunks
- Markdown estructurado en respuestas

---

## Notas

- **Todos los comandos solo funcionan para el usuario especificado en `.env` (TELEGRAM_USER_ID)**
- **Los comandos que modifiquen datos (`/clear_history`, `/forget_all`) son irreversibles**
- **`/compact` es seguro — solo optimiza el archivo sin perder datos**
- **`/exec` captura hasta 4000 caracteres de salida**
- **Las imágenes se analizan pero no se retornan en respuestas** (Claude analiza, no envía imágenes)

## Diferencia: Comandos vs Conversación

| Forma | Comportamiento |
|-------|----------------|
| **Mensaje normal** | Alex procesa como conversación, puede usar herramientas |
| **Comando `/...`** | Comando directo, sin pasar por Alex, ejecución inmediata |

**Ejemplo:**
- Mensaje: `"ejecuta dir C:\\"` → Alex decide si usar `execute_command` o simplemente responder
- Comando: `/exec dir C:\\` → ejecuta directamente sin procesamiento por Alex

---

**Última actualización:** 2026-07-03
