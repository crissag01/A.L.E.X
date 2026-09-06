#!/usr/bin/env python3
"""Test rapido del sistema de control de acceso"""

import sqlite3
import os
from Memory import db as memory_db
from Tools.access_control import check_access, approve_user, reject_user

print("=" * 60)
print("TEST: Sistema de Control de Acceso")
print("=" * 60)

# 1. Inicializar BD
print("\n1. Inicializando base de datos...")
memory_db.init_db()
# Limpiar tabla de usuarios aprobados para tests limpios
conn = sqlite3.connect("Memory/alex.db")
conn.execute("DELETE FROM approved_users")
conn.commit()
conn.close()
print("[OK] BD inicializada y limpiada")

# 2. Ver tabla approved_users
print("\n2. Verificando tabla approved_users...")
conn = sqlite3.connect("Memory/alex.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='approved_users'")
exists = cursor.fetchone()
if exists:
    print("[OK] Tabla approved_users existe")
else:
    print("[ERROR] Tabla approved_users NO existe")
    exit(1)

# 3. Test check_access para usuario nuevo
print("\n3. Test: Usuario nuevo (no existe)...")
allowed, status = check_access(999999)
print(f"   User 999999 -> allowed={allowed}, status={status}")
assert status == "new", f"Esperaba 'new', recibí '{status}'"
print("[OK] Usuario nuevo correctamente identificado")

# 4. Test approve_user
print("\n4. Test: Aprobar usuario...")
approve_user(999999, "test_user", "Auto-aprobado para test")
allowed, status = check_access(999999)
print(f"   User 999999 despues -> allowed={allowed}, status={status}")
assert allowed == True, f"Esperaba allowed=True"
assert status == "approved", f"Esperaba 'approved', recibí '{status}'"
print("[OK] Usuario aprobado correctamente")

# 5. Test reject_user
print("\n5. Test: Rechazar usuario...")
reject_user(888888, "spam_bot", "Detectado como spam")
allowed, status = check_access(888888)
print(f"   User 888888 -> allowed={allowed}, status={status}")
assert allowed == False, f"Esperaba allowed=False"
assert status == "rejected", f"Esperaba 'rejected', recibí '{status}'"
print("[OK] Usuario rechazado correctamente")

# 6. Ver registros en BD
print("\n6. Registros en approved_users:")
cursor.execute("SELECT telegram_user_id, username, alex_decision FROM approved_users")
rows = cursor.fetchall()
for user_id, username, decision in rows:
    print(f"   * {user_id} (@{username}) -> {decision}")
conn.close()

print("\n" + "=" * 60)
print("[EXITO] TODOS LOS TESTS PASARON")
print("=" * 60)
print("\nSistema de control de acceso: OPERACIONAL")
print("Alex es el portero de Cris. Otros usuarios necesitan aprobacion.")
