"""Manejadores de comandos Telegram"""
import subprocess
import sqlite3
from Memory import db as memory_db
from Memory import reminder_manager


def handle_command(text, chat_id, send_message_fn):
    """Procesa comandos Telegram (/, comando, argumentos)"""
    parts = text.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/help":
        msg = """Comandos disponibles:
/help - Este mensaje
/stats - Ver estadisticas (memoria, turnos, recordatorios)
/compact - Compactar base de datos
/clear_history - Borrar historial de esta conversacion
/list_reminders - Ver recordatorios pendientes
/memory - Ver ultimas memorias guardadas
/exec <comando> - Ejecutar comando CLI directamente
/forget_all - Borrar TODAS las memorias (irreversible)
/status - Estado del sistema"""
        send_message_fn(chat_id, msg)

    elif cmd == "/stats":
        try:
            conn = sqlite3.connect('Memory/alex.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversation_turns WHERE channel='telegram'")
            turns = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM facts")
            facts = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM reminders WHERE sent=0")
            reminders = cursor.fetchone()[0]
            conn.close()
            msg = f"""Estadisticas de Alex:
* Turnos en canal Telegram: {turns}
* Memorias almacenadas: {facts}
* Recordatorios pendientes: {reminders}"""
            send_message_fn(chat_id, msg)
        except Exception as e:
            send_message_fn(chat_id, f"Error al leer estadisticas: {e}")

    elif cmd == "/compact":
        try:
            conn = sqlite3.connect('Memory/alex.db')
            conn.execute("PRAGMA optimize;")
            conn.execute("VACUUM;")
            conn.close()
            send_message_fn(chat_id, "OK: Base de datos compactada exitosamente")
        except Exception as e:
            send_message_fn(chat_id, f"Error al compactar: {e}")

    elif cmd == "/clear_history":
        try:
            conn = sqlite3.connect('Memory/alex.db')
            conn.execute("DELETE FROM conversation_turns WHERE channel='telegram'")
            conn.commit()
            conn.close()
            send_message_fn(chat_id, "OK: Historial de Telegram borrado")
        except Exception as e:
            send_message_fn(chat_id, f"Error: {e}")

    elif cmd == "/list_reminders":
        try:
            reminders = reminder_manager.list_pending_reminders()
            if not reminders:
                send_message_fn(chat_id, "OK: No hay recordatorios pendientes")
            else:
                msg = "Recordatorios pendientes:\n"
                for r in reminders:
                    msg += f"* ID {r['id']}: {r['message']} (a las {r['due_at']})\n"
                send_message_fn(chat_id, msg)
        except Exception as e:
            send_message_fn(chat_id, f"Error: {e}")

    elif cmd == "/memory":
        try:
            conn = sqlite3.connect('Memory/alex.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, text FROM facts ORDER BY last_accessed_at DESC LIMIT 10")
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                send_message_fn(chat_id, "OK: No hay memorias guardadas")
            else:
                msg = "Ultimas 10 memorias:\n"
                for idx, (fid, text) in enumerate(rows, 1):
                    msg += f"{idx}. [{fid}] {text[:80]}\n"
                send_message_fn(chat_id, msg)
        except Exception as e:
            send_message_fn(chat_id, f"Error: {e}")

    elif cmd == "/exec":
        if not args:
            send_message_fn(chat_id, "Uso: /exec <comando>\nEjemplo: /exec dir C:\\")
            return
        try:
            result = subprocess.run(args, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout or result.stderr or "(sin salida)"
            if len(output) > 4000:
                output = output[:4000] + "\n...(truncado)"
            msg = f"Ejecutado:\n```\n{output}\n```"
            send_message_fn(chat_id, msg)
        except subprocess.TimeoutExpired:
            send_message_fn(chat_id, "Timeout: el comando tardo mas de 30 segundos")
        except Exception as e:
            send_message_fn(chat_id, f"Error al ejecutar: {e}")

    elif cmd == "/forget_all":
        try:
            conn = sqlite3.connect('Memory/alex.db')
            conn.execute("DELETE FROM facts")
            conn.commit()
            conn.close()
            send_message_fn(chat_id, "OK: TODAS las memorias han sido borradas (irreversible)")
        except Exception as e:
            send_message_fn(chat_id, f"Error: {e}")

    elif cmd == "/status":
        try:
            conn = sqlite3.connect('Memory/alex.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversation_turns")
            total_turns = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM facts")
            total_facts = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM reminders WHERE sent=0")
            pending_reminders = cursor.fetchone()[0]
            conn.close()
            msg = f"""Estado del sistema:
* Total de turnos: {total_turns}
* Total de memorias: {total_facts}
* Recordatorios pendientes: {pending_reminders}
* Modelo: Claude Sonnet 5
* Extended Thinking: ON
* Persistencia: SQLite WAL"""
            send_message_fn(chat_id, msg)
        except Exception as e:
            send_message_fn(chat_id, f"Error: {e}")

    else:
        send_message_fn(chat_id, f"Comando desconocido: {cmd}\nUsa /help para ver comandos disponibles")
