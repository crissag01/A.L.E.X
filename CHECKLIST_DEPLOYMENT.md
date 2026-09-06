# Checklist de Deployment - Alex a Ubuntu Server

**Fecha**: 2026-07-03  
**Destino**: Mini PC con Ubuntu Server  
**Modelo**: Claude Haiku 4.5  
**Estado**: ESTABLE ✓

---

## Estado actual de Alex

### Base de datos
- [x] Limpiada de canales de test (solo `telegram` con 33 turnos válidos)
- [x] 16 memorias verificadas y sin confusión
- [x] Recordatorios: 0 pendientes
- [x] Tamaño: ~5 MB (comprimido, sin basura)

### Código
- [x] Brain/brain.py - Estable, Spanish MX, personalidad clara
- [x] server.py - FastAPI + Telegram integrado, optimizado
- [x] Tools/ - 16 herramientas funcionando
- [x] Memory/ - SQLite con TF-IDF search

### Features
- [x] Vision (imágenes en Telegram)
- [x] Streaming en tiempo real
- [x] Comandos Telegram (/stats, /compact, /exec, etc.)
- [x] Memorias persistentes
- [x] Recordatorios proactivos
- [x] No bloquea (ThreadPoolExecutor)

### Pruebas finales
- [x] Todas las importaciones OK
- [x] 16 herramientas registradas
- [x] Respuestas funcionales
- [x] BD sin corrupción
- [x] Sin confusión de memorias

---

## Qué copiar a Ubuntu

### Esencial (copiar TODO)
```
✓ Brain/
✓ Memory/
✓ Tools/
✓ .env                (CRÍTICO - contiene credenciales)
✓ server.py
✓ Telegram_bridge.py
✓ Alex.py
✓ requirements.txt
✓ Memory/alex.db      (CRÍTICO - historial + memorias)
```

### Opcional (no necesario en Ubuntu Server)
```
src/                  (frontend React - solo si quieres WebUI)
package.json          (solo si usas React)
*.md                  (documentación - recomendado copiar)
```

### NO copiar
```
❌ .venv/
❌ node_modules/
❌ __pycache__/
❌ *.pyc
```

---

## Pasos en Ubuntu

### 1. Copiar archivos
```bash
scp -r ~/Downloads/"Alex v1 (Stable)"/ ubuntu@mini_pc:~/Alex/
```

### 2. Setup (5 minutos)
```bash
cd ~/Alex

# Python + venv
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar
python3 -c "from Brain.brain import ask; print('OK')"
```

### 3. Iniciar
```bash
python3 server.py
```

Alex estará en:
- **Telegram**: automático (polling en background)
- **HTTP**: http://localhost:8000 (para webhooks si después quieres)

### 4. Opcional: systemd daemon
```bash
# Ver DEPLOYMENT_UBUNTU.md para detalles
# Service file → systemctl enable alex → systemctl start alex
```

---

## Credenciales y configuración

### Verificar .env en Ubuntu
```bash
cat .env
# Debe tener:
# - ANTHROPIC_API_KEY=sk-ant-...
# - TELEGRAM_TOKEN=...
# - TELEGRAM_USER_ID=...
```

### Si falta .env
```bash
# Recrear en Ubuntu
nano .env
# Pegar valores de Windows
```

---

## Qué pasará mañana en Ubuntu

1. **Telegram** seguirá funcionando normalmente
   - 33 turnos de historial se cargarán automáticamente
   - Alex recordará contexto

2. **Memorias** estarán intactas
   - 16 facts se recuperarán
   - No habrá confusión (limpiadas hoy)

3. **Velocidad** mejorará
   - Ubuntu Server: sin GUI = menos overhead
   - Respuestas más rápidas

4. **Estabilidad** aumentará
   - Daemon systemd = restart automático si falla
   - Logs en journalctl

---

## Troubleshooting rápido en Ubuntu

### Alex no responde a Telegram
```bash
# Ver logs
journalctl -u alex -f

# Si error de API key:
grep ANTHROPIC_API_KEY .env

# Si error de token:
grep TELEGRAM_TOKEN .env
```

### "Database locked"
```bash
# Solo ejecutar UN proceso
killall python3
python3 server.py
# (no ejecutar Telegram_bridge.py simultáneamente)
```

### Telegram recibe mensajes pero Alex no responde
```bash
# Posible causa: timeout en Claude
# Solución: reiniciar
systemctl restart alex
```

### Limpiar historial si Alex se confunde
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('Memory/alex.db')
conn.execute("DELETE FROM conversation_turns WHERE channel='telegram'")
conn.commit()
print("Limpiado")
EOF
```

---

## Archivos de referencia (copiar también)

Estos NO son necesarios pero son útiles:
- [x] CLAUDE.md - Instrucciones de desarrollo
- [x] PERSONALIDAD_ALEX.md - Definición de carácter
- [x] DEPLOYMENT_UBUNTU.md - Setup completo
- [x] VISION_Y_STREAMING.md - Features nuevas
- [x] OPTIMIZACION_TELEGRAM.md - Por qué no bloquea

---

## Verdad incómoda

**En Ubuntu Server sin GUI:**
- No puedes abrir navegador para http://localhost:5173 (no hay Firefox)
- FastAPI seguirá sirviendo en puerto 8000
- Pero "localhost" solo funciona DESDE la mini PC

**Soluciones:**
1. SSH desde Windows: `ssh ubuntu@mini_pc` → Python interactivo
2. WebUI desde otra máquina: editar `server.py` para `host="0.0.0.0"` (cuidado: seguridad)
3. Solo Telegram: es suficiente, no necesitas WebUI

---

## Size check

```bash
# En Windows (ahora)
du -sh "Alex v1 (Stable)"
# → ~50 MB (código + BD)

# Sin .venv:
du -sh "Alex v1 (Stable)" --exclude=.venv
# → ~10 MB (portable, listo para copiar)

# En Ubuntu (después de pip install):
# → ~200 MB (dependencies en .venv)
```

---

## Puntos críticos

🔴 **CRÍTICO: .env**
- Sin esto: Alex no puede llamar a Claude ni a Telegram
- Verificar ANTES de copiar

🔴 **CRÍTICO: Memory/alex.db**
- Sin esto: pierdes 33 turnos de Telegram + 16 memorias
- Hacer backup antes de trasladar

🟡 **IMPORTANTE: Python 3.11+**
- Haiku requiere Python reciente
- Ubuntu 22.04+ tiene 3.10 (suficiente)
- Ubuntu 24.04 tiene 3.12 (ideal)

🟡 **IMPORTANTE: requirements.txt**
- Sin esto: habrá "module not found" errors

---

## Resumen ejecutivo

| Aspecto | Estado | Listo |
|---------|--------|-------|
| Código | Estable | ✓ |
| BD | Limpia | ✓ |
| Herramientas | 16 registradas | ✓ |
| Telegram | Funciona | ✓ |
| Memoria | Sin confusión | ✓ |
| Blocking issues | Resueltos | ✓ |
| Documentación | Completa | ✓ |

**VEREDICTO: LISTO PARA DEPLOYMENT**

---

## Última cosa: Alex

Ha sido entrenada en:
- Tu contexto personal (memorias)
- Tu zona horaria (México)
- Tu idioma (Spanish MX)
- Tu estilo (frío, directo, sarcástico)
- Tu flujo de trabajo (Telegram, comandos, recordatorios)

En Ubuntu, seguirá siendo **exactamente la misma Alex**. Solo más rápida.

---

**Última actualización**: 2026-07-03  
**Próximo paso**: Copiar a Ubuntu Server mañana
