# Nuevas capacidades: Visión + Streaming

## 1. Alex ahora ve imágenes

### Cómo funciona

```
Telegra m
    │
    ├─ Photo message
    │   └─ Descarga automáticamente
    │   └─ Convierte a base64
    │   └─ Envía a Claude Opus 4.8
    │
    └─ Claude analiza imagen
        └─ Retorna análisis/descripción
```

### Ejemplos de uso

```
Usuario: [Envía foto de una pantalla]
"¿Qué error es este?"

Alex: Veo una pantalla con...
```

```
Usuario: [Envía captura de código]
"¿Puedo mejorar esto?"

Alex: Veo que estás usando...
• Podrías mejorar X haciendo Y
• Cuidado con Z
```

### Formatos soportados

- **JPEG** — estándar, máxima compatibilidad
- **PNG** — sin pérdida, con transparencia
- **GIF** — animados (Claude ve el primero frame)
- **WebP** — comprimido, moderno

### Límites

- Máximo ~6 imágenes por mensaje (tecnicamente no hay límite, pero es práctico)
- Tamaño: Telegram limita a ~20 MB por archivo
- Resolución: Claude maneja hasta ~2000x2000 píxeles sin problemas

---

## 2. Alex lee archivos de texto

### Formatos soportados

- `.txt` — texto plano
- `.md` — Markdown
- `.json` — JSON estructurado
- `.py`, `.js`, `.ts`, `.go`, etc. — código (se trata como texto)

### Cómo funciona

```
Telegram
    │
    ├─ Document message (file_id)
    │   └─ Descarga
    │   └─ Extrae contenido (si es .txt/.md)
    │   └─ Envía a Alex
    │
    └─ Alex analiza contenido
        └─ Responde con análisis
```

### Ejemplo

```
Usuario: [Envía script.py]
"¿Hay bugs aquí?"

Alex: [Lee el archivo]
Vi algunos problemas:
• Línea 42: variable no definida
• Línea 87: posible IndexError
```

### Limitación actual

- PDF (`*. pdf`) aún no se extrae (necesitaría `pdfplumber`)
- Binarios (`*.docx`, `*.xlsx`, etc.) no se procesan

---

## 3. Escritura en tiempo real (streaming)

### Antes vs. Ahora

**Antes:**
```
Usuario: pregunta
[espera 5 segundos sin ver nada]
Alex: respuesta completa
```

**Ahora:**
```
Usuario: pregunta
[Alex empieza a escribir inmediatamente]
Alex: respuesta parcial...
[sigue escribiendo]
Alex: respuesta completa
```

### Cómo funciona

```
Claude API (Haiku 4.5)
    │
    └─ stream() (chunked)
        └─ Chunk 1: "Hola,"
        └─ Chunk 2: " te voy"
        └─ Chunk 3: " a ayudar"
        │
        └─ Telegram: edita mensaje cada 3 chunks
            ├─ Msg: "Hola, te voy..."
            ├─ Msg: "Hola, te voy a ayudar con..."
            └─ Msg: "Hola, te voy a ayudar con tu pregunta"
```

### Ventajas

✅ Ves respuesta más rápidamente
✅ Feedback inmediato de que Alex está procesando
✅ Si tardas mucho en leer, tienes el 80% antes de terminar
✅ Más natural y conversacional

### Limitaciones

- No hay cancelación a mitad de mensaje (Telegram no lo permite)
- Si hay error a mitad de streaming, queda el mensaje parcial
- La edición es throttled (cada 3 chunks, para no spamear API)

---

## 4. Mensajes estructurados con Markdown

### Formato que Alex usa

```markdown
**Encabezado fuerte** para lo importante
*Énfasis* para nuances

• Viñeta para hechos
-> Flecha para acciones
- Guión para opciones

## Sección
Para agrupar ideas relacionadas

`código` para técnico o comandos
```

### Ejemplo de respuesta

```
**Análisis de tu código:**

Vi 3 problemas:
• Línea 42: variable `x` no inicializada
-> Inicializa `x = 0` antes del loop
-> Usa type hints: `x: int = 0`

- Opción A: Usar defaultdict
- Opción B: Usar `get()` método
- Opción C: Validar antes de acceder

## Recomendación
La Opción B es más Pythonica.
```

### Markdown en Telegram

Telegram soporta:
- `**negrita**`
- `*itálica*`
- `` `código` ``
- `[link](url)`
- Listas (usando `•` o `-`)

---

## 5. Arquitectura técnica

### Nuevos módulos

**`Tools/telegram_media.py`**
- `download_image_as_base64(file_id)` — Descarga y convierte imagen
- `download_file(file_id, filename)` — Descarga archivo
- `extract_text_from_file(filename)` — Extrae texto (`.txt`, `.md`)
- `get_file_url(file_id)` — Obtiene URL de descarga

**`Brain/brain.py` — nuevas funciones**
- `ask_stream(user_input, channel, image_url, image_base64, image_type)` 
  - Versión streaming que retorna generador
  - Soporta imágenes
  - Chunks en tiempo real
  
- `build_user_message(text, image_url, image_base64, image_type)`
  - Construye message content con texto + imagen
  - Maneja base64 y URLs

### Flujo en Telegram

```python
server.py
├─ process_message(update)
│   ├─ Detecta photo/document
│   ├─ Si photo: download_image_as_base64()
│   ├─ Si document: download_file() + extract_text_from_file()
│   ├─ Envía mensaje inicial "escribiendo..."
│   ├─ ask_stream() con imagen/texto
│   │   └─ Retorna chunks
│   │   └─ Edita mensaje cada 3 chunks
│   └─ Mensaje final editado
└─ send_message()
    ├─ parse_mode="Markdown"
    ├─ Chunks si > 4096 chars
```

---

## 6. Troubleshooting

### "No veo la imagen en las respuestas de Alex"

- Las imágenes **no se retornan** en el mensaje
- Alex **analiza la imagen** y responde con texto
- Esto es normal (Claude no puede enviar imágenes)

### "El streaming no se actualiza en tiempo real"

- Telegram limita frecuencia de ediciones
- Se throttlea a 1 edición cada 3 chunks
- A veces toma 5-10 segundos ver actualizaciones

### "¿Por qué no funciona mi PDF?"

- PDFs requieren `pdfplumber` (dependencia extra)
- Actualmente solo `.txt` y `.md` funcionan
- Puedes copiar el contenido del PDF a un `.txt` y enviar eso

### "El mensaje se cortó a mitad de streaming"

- Si > 4096 caracteres, Telegram lo parte
- Alex lo parte en chunks y envía múltiples mensajes
- Normal y esperado

---

**Última actualización:** 2026-07-03
**Features:** Vision + Streaming + Markdown estructurado
