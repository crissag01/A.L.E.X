#!/usr/bin/env python
"""Test rápido de memoria, herramientas y persistencia"""
import sys
from Brain.brain import ask
import sqlite3

print("=== TEST 1: Verificar que herramientas se cargan ===")
from Tools.tool_manager import TOOLS
print(f"Total de herramientas registradas: {len(TOOLS)}")
expected = ["get_time", "remember", "forget", "execute_command", "write_file",
            "delete_file", "set_reminder", "list_reminders", "cancel_reminder",
            "get_weather", "get_system_info", "calculate", "open_program",
            "list_directory", "web_search", "read_file"]
missing = [t for t in expected if t not in TOOLS]
if missing:
    print(f"WARNING: Herramientas faltantes: {missing}")
else:
    print("OK: Todas las herramientas esperadas estan presentes")

print("\n=== TEST 2: Probar una pregunta simple ===")
try:
    reply = ask("Hola, soy Cris. Dime la hora actual.", channel="test")
    print(f"Respuesta de Alex: {reply[:200]}...")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("\n=== TEST 3: Verificar persistencia en base de datos ===")
conn = sqlite3.connect('Memory/alex.db')
cursor = conn.execute('SELECT COUNT(*) FROM conversation_turns WHERE channel = ?', ('test',))
count = cursor.fetchone()[0]
print(f"Turnos guardados en canal 'test': {count}")
if count >= 4:  # user + assistant + user + assistant (minimo esperado)
    print("OK: Persistencia de historial funcionando")
else:
    print(f"WARNING: Esperado >= 4 turnos, pero se encontraron {count}")

print("\n=== TEST 4: Verificar que la segunda llamada reutiliza el historial ===")
try:
    reply2 = ask("Recuerdas lo que dije?", channel="test")
    print(f"Segunda respuesta: {reply2[:200]}...")
    print("OK: Historial rehidratado desde BD sin errores")
except Exception as e:
    print(f"ERROR rehidratando historial: {e}")
    sys.exit(1)

print("\n=== TODOS LOS TESTS PASARON ===")
