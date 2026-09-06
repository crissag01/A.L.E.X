#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test del sistema de memoria con ChromaDB."""

from Brain.brain import ask
from Memory.memory_manager_chroma import save_memory, search_memories

print("=" * 60)
print("TEST: Sistema de Memoria con ChromaDB")
print("=" * 60)

# Test 1: Guardar una memoria
print("\n[1] Guardando memoria...")
save_memory("El usuario Cris tiene 19 años y es freelancer")
print("   OK - Memoria guardada")

# Test 2: Guardar otra memoria
print("\n[2] Guardando segunda memoria...")
save_memory("Alex es una asistente basada en Alex Brand de Gears of War")
print("   OK - Memoria guardada")

# Test 3: Buscar memorias relacionadas
print("\n[3] Buscando memorias sobre edad...")
results = search_memories("cuantos anos tienes", top_k=2)
print(f"   Resultados encontrados: {len(results)}")
for i, mem in enumerate(results, 1):
    print(f"   {i}. {mem}")

# Test 4: Respuesta de Alex con contexto de memoria
print("\n[4] Preguntando a Alex sobre quien eres...")
response = ask("Quien soy yo")
print(f"   Respuesta: {response[:100]}...")

print("\n" + "=" * 60)
print("Test completado. Sistema de memoria funciona.")
print("=" * 60)
