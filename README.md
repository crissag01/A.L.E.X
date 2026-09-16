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

## Licencia y uso del código

Este repositorio **no cuenta con ninguna licencia de código abierto**. Todos los derechos están reservados. El uso, clonación, fork, copia, redistribución o modificación de este código sin autorización expresa y por escrito del autor está **estrictamente prohibido** y será objeto de las acciones legales correspondientes.

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
