# Alex Frontend v0.2 - React Dashboard

Frontend React para Alex con backend FastAPI. Diseño oscuro, directo, sin bloat.

## Estructura

```
.
├── src/
│   ├── AlexDashboard.jsx       # Componente React principal
│   └── main.jsx                 # Entry point
├── api.py                       # Backend FastAPI
├── index.html                   # HTML root
├── package.json                 # Dependencias Node
└── vite.config.js              # Config Vite
```

## Setup

### 1. Backend FastAPI

Requisitos previos:
- Python 3.11+
- `brain.py` existente en el mismo directorio (o ajustar import)
- Ollama/LM Studio corriendo en `localhost:1234/v1`

Instalar dependencias:
```bash
pip install fastapi uvicorn psutil --break-system-packages
```

Ejecutar:
```bash
python api.py
```

El backend estará en `http://127.0.0.1:8000`

Health check: `curl http://127.0.0.1:8000/health`

### 2. Frontend React

Requisitos:
- Node.js 18+
- npm/pnpm/yarn

Instalar dependencias:
```bash
npm install
# o
pnpm install
```

Ejecutar en desarrollo:
```bash
npm run dev
```

Abre automáticamente en `http://localhost:5173`

### 3. Flujo completo

Terminal 1 (Backend):
```bash
python api.py
```

Terminal 2 (Frontend):
```bash
npm run dev
```

Abre navegador → `http://localhost:5173`

## Endpoints

### POST `/api/chat`
Envía un mensaje, obtiene respuesta de Alex.

Request:
```json
{ "message": "¿Qué hora es?" }
```

Response:
```json
{ "reply": "Son las 14:32" }
```

### GET `/api/stats`
Obtiene stats del sistema (CPU, RAM, modelo).

Response:
```json
{
  "cpu": 23,
  "ram": "7.9 / 16 GB",
  "model": "qwen:7b",
  "connected": true
}
```

### GET `/health`
Health check del backend.

## Personalización

### Cambiar colores
En `AlexDashboard.jsx`, editar valores hex:
- `#00d9a3` → acento verde (cambiar a tu color)
- `#1a1a1a` → surfaces
- `#0a0a0a` → fondo

### Cambiar endpoint backend
En `AlexDashboard.jsx`, línea ~70:
```javascript
const response = await fetch('http://127.0.0.1:8000/api/chat', {
```

### Agregar más secciones al sidebar
En `AlexDashboard.jsx`, modificar array `menuItems`:
```javascript
const menuItems = [
  { section: 'Core', items: ['Alex Core', 'Mi nuevo item'] },
  // ...
];
```

## Troubleshooting

**"Backend no disponible"**
- ¿Levantó `api.py`?
- ¿Corre en `localhost:8000`?
- Verificar CORS en consola del navegador

**"Error: Cannot find module 'brain'"**
- `api.py` debe estar en el mismo directorio que `brain.py`
- O ajustar `sys.path.insert(0, '/path/to/brain')`

**React no carga**
- Verificar que `npm install` corrió sin errores
- `node_modules/.vite` existe?
- Prueba `npm run dev` de nuevo

**Stats siempre en 0**
- ¿`psutil` instalado? `pip install psutil`
- ¿Ollama/LM Studio corriendo?

## Build para producción

```bash
npm run build
```

Genera carpeta `dist/` lista para deployment.

## Desarrollo

Hot reload automático en cambios de `.jsx`

Stats se actualizan cada 3 segundos

Mensajes con animación suave

Manejo de errores en conexión a backend

## Notas

- Monoespaciada (JetBrains Mono) para código/stats
- Sin gradientes, sombras, ni efectos innecesarios
- Scroll automático al último mensaje
- Loading state mientras espera respuesta
- Conexión WebSocket ready para upgrade futuro
