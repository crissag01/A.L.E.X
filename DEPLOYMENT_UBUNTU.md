# Deployment de Alex en Ubuntu Server

## Preparación previa (antes de trasladar)

### En Windows (ahora)
✅ BD limpiada (solo canal `telegram` con 33 turnos)
✅ 16 memorias (facts) limpias y verificadas
✅ Código estable en `main` branch
✅ Dependencias documentadas

## Archivos a copiar a Ubuntu

### Esencial (todo el proyecto)
```
Alex v1 (Stable)/
├── Brain/
├── Memory/
├── Tools/
├── src/                    # Frontend React (opcional)
├── .env                    # Variables de entorno (IMPORTANTE)
├── server.py              # Backend principal
├── Telegram_bridge.py     # Polling Telegram (fallback)
├── Alex.py                # CLI (fallback)
├── requirements.txt       # Dependencias Python
├── package.json           # Dependencias Node (si usas React)
└── Memory/alex.db         # Base de datos SQLite (con historial)
```

### Importante: NO copiar
```
❌ .venv/               # Virtual env (recrear en Ubuntu)
❌ node_modules/        # Dependencias Node (reinstalar)
❌ __pycache__/         # Cachés Python (regenerarse)
```

## Setup en Ubuntu Server

### 1. Copiar archivos
```bash
# Desde Windows (en WSL o desde otra máquina):
scp -r "Alex v1 (Stable)/" ubuntu_user@mini_pc:~/Alex/
```

### 2. Instalar Python y dependencias
```bash
cd ~/Alex

# Python 3.11+ (importante: Haiku requiere versión reciente)
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Crear virtual env
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Instalar Node.js (opcional, si usas React)
```bash
# Si necesitas frontend
sudo apt install -y nodejs npm

# En directorio del proyecto
npm install
```

### 4. Configurar variables de entorno
```bash
# Copiar .env a Ubuntu (CRÍTICO)
# Contiene:
# - ANTHROPIC_API_KEY
# - TELEGRAM_TOKEN
# - TELEGRAM_USER_ID

# Crear o editar .env
nano .env

# Verificar que sea readable:
ls -la .env  # Debería ser -rw-r--r-- (600)
```

### 5. Verificar instalación
```bash
# Test de importación
python3 -c "from Brain.brain import ask; print('OK')"

# Test de BD
python3 -c "import sqlite3; conn = sqlite3.connect('Memory/alex.db'); print('DB OK')"

# Ver turnos existentes
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('Memory/alex.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM conversation_turns WHERE channel='telegram'")
print(f"Turnos en Telegram: {cursor.fetchone()[0]}")
conn.close()
EOF
```

## Iniciar en Ubuntu

### Opción 1: FastAPI + Telegram integrado (RECOMENDADO)
```bash
source .venv/bin/activate
python3 server.py
```

Accederá a:
- Backend: `http://localhost:8000`
- Chat: `http://localhost:8000/chat` (POST)

### Opción 2: CLI (debugging)
```bash
source .venv/bin/activate
python3 Alex.py
```

### Opción 3: Telegram separado (si necesitas debug)
```bash
# Terminal 1
python3 server.py

# Terminal 2
python3 Telegram_bridge.py
```

## Optimizaciones para Ubuntu Server (sin GUI)

### 1. Ejecutar como daemon con systemd
```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/alex.service

# Pegar:
[Unit]
Description=Alex Personal Agent
After=network.target

[Service]
Type=simple
User=ubuntu_user
WorkingDirectory=/home/ubuntu_user/Alex
Environment="PATH=/home/ubuntu_user/Alex/.venv/bin"
ExecStart=/home/ubuntu_user/Alex/.venv/bin/python3 server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# Habilitar y iniciar
sudo systemctl enable alex
sudo systemctl start alex

# Ver estado
sudo systemctl status alex

# Logs
journalctl -u alex -f  # tiempo real
journalctl -u alex -n 50  # últimas 50 líneas
```

### 2. Puerto seguro con firewall
```bash
# Permitir puerto 8000 (opcional, si expones al exterior)
sudo ufw allow 8000

# O solo localhost (recomendado para uso personal)
# Editar server.py: uvicorn.run(..., host="127.0.0.1", port=8000)
```

### 3. Monitoreo de recursos
```bash
# Instalar htop para monitorear
sudo apt install htop
htop  # Ver CPU/RAM en tiempo real

# O comando simple
watch -n 1 'ps aux | grep python3'
```

## Respaldo de datos

### Backup de BD antes de trasladar
```bash
# En Windows
cp Memory/alex.db Memory/alex.db.backup

# Copiar ambas a Ubuntu
```

### Backup periódico en Ubuntu
```bash
# Script simple
#!/bin/bash
cp ~/Alex/Memory/alex.db ~/Alex/Memory/alex.db.backup.$(date +%Y%m%d)

# Ejecutar diariamente con cron
crontab -e
# Agregar:
# 0 2 * * * /home/ubuntu_user/backup_alex.sh
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
source .venv/bin/activate
pip install anthropic
```

### "SQLite database is locked"
```bash
# Significa que dos procesos acceden simultáneamente
# Solución: ejecutar solo UN process (server.py, NO Telegram_bridge.py)
```

### Telegram no responde
```bash
# Ver logs
journalctl -u alex -f

# Verificar .env tiene TELEGRAM_TOKEN y TELEGRAM_USER_ID correctos
cat .env | grep TELEGRAM
```

### Memoria confusa / hallucinations
```bash
# Si Alex confunde contextos, limpiar canal específico:
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('Memory/alex.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM conversation_turns WHERE channel='telegram'")
conn.commit()
print("Historial de Telegram limpiado")
conn.close()
EOF
```

## Tamaño de la BD

```bash
# Ver tamaño de alex.db
ls -lh Memory/alex.db

# Típico: 5-50 MB (dependiendo de cuántos turnos)

# Si crece mucho (> 100 MB), limpiar:
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('Memory/alex.db')
conn.execute("VACUUM;")  # Compacta
conn.close()
EOF
```

## Checklist previo a trasladar

- [ ] `.env` con credentials correctas
- [ ] `Memory/alex.db` copiado (con historial)
- [ ] `requirements.txt` actualizado
- [ ] Test en Windows: `python test_system.py` ✅
- [ ] BD limpiada de canales de test
- [ ] Documentación leída (CLAUDE.md, PERSONALIDAD_ALEX.md)
- [ ] Backup de `Memory/alex.db` guardado

## Checklist en Ubuntu

- [ ] Python 3.11+ instalado
- [ ] Virtual env activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] `.env` en lugar correcto
- [ ] `Memory/alex.db` copiado
- [ ] Test: `python3 -c "from Brain.brain import ask; print('OK')"`
- [ ] FastAPI inicia sin errores: `python3 server.py`
- [ ] Telegram responde a mensajes
- [ ] systemd service configurado (opcional pero recomendado)

---

**Fecha**: 2026-07-03
**Destino**: Ubuntu Server (mini PC)
**Modelo**: Claude Haiku 4.5
**BD**: SQLite (portable, sin dependencias)
