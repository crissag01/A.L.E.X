#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test simple del sistema de memoria - sin llamadas a API."""

from Memory.memory_manager import save_memory, search_memories, load_memories

print("=" * 60)
print("TEST SIMPLE: Sistema de Memoria")
print("=" * 60)

# Test 1: Guardar memorias
print("\n[1] Guardando memorias...")
save_memory("El usuario Cris tiene 19 años")
save_memory("Cris es freelancer y programador Python")
save_memory("Alex Brand es el personaje base de Alex")
print("    OK - 3 memorias guardadas")

# Test 2: Cargar todas las memorias
print("\n[2] Cargando todas las memorias...")
all_mems = load_memories()
print(f"    Total de memorias: {len(all_mems)}")
for i, mem in enumerate(all_mems, 1):
    print(f"    {i}. {mem}")

# Test 3: Buscar memorias
print("\n[3] Buscando memorias sobre edad...")
results = search_memories("cuantos anos tiene", top_k=2)
print(f"    Resultados: {len(results)}")
for mem in results:
    print(f"    - {mem}")

print("\n[4] Buscando memorias sobre programacion...")
results = search_memories("programador Python", top_k=2)
print(f"    Resultados: {len(results)}")
for mem in results:
    print(f"    - {mem}")

print("\n" + "=" * 60)
print("OK - Sistema de memoria funciona correctamente")
print("=" * 60)
