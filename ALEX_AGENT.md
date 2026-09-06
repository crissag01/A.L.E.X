# Alex - Tu Agente Personal Agentic

Alex es tu agente personal singular, no un orquestador de múltiples agentes. Funciona como una entidad autónoma enfocada completamente en ti.

## Cómo funciona

### El flujo de Alex

```
Tu mensaje
    ↓
[Razonamiento profundo con Extended Thinking]
    ↓
[Análisis: ¿Necesito herramientas? ¿Información de memoria?]
    ↓
[Ejecución autónoma de herramientas si es necesario]
    ↓
[Respuesta fundamentada + contexto usado]
```

### Características Agentic

1. **Extended Thinking Adaptativo**
   - Alex piensa profundamente antes de responder
   - Explora múltiples ángulos del problema
   - Tu pensamiento es invisible (pero sucede)

2. **Herramientas Autónomas**
   - Alex decide cuándo usar herramientas
   - No espera permiso
   - Ejecuta según su propio criterio

3. **Memoria Integrada**
   - Las memorias relevantes se incluyen automáticamente
   - Contexto histórico enriquece el razonamiento

4. **Modelo Potente**
   - Claude Opus 4.8 (el más capaz)
   - 8k tokens por respuesta
   - Mejor razonamiento que cualquier modelo anterior

## Herramientas disponibles

```
- get_time: Hora actual del sistema
- remember: Guardar información en memoria persistente
- open_program: Abrir aplicaciones (notepad, calculator, explorer)
- list_directory: Explorar directorios
- web_search: Buscar en internet
- read_file: Leer archivos
```

## Personalidad

Alex es **directo, escéptico, cynical**. Busca constantemente:
- Manipulación emocional
- Señales de fraude
- Agendas ocultas
- Inconsistencias

Pero **cambia de tono** si realmente estás en problemas.

## Cómo empezar

**Opción A: WebUI (recomendado)**
```bash
# Terminal 1
python server.py

# Terminal 2
npm run dev

# Abre http://localhost:5173
```

**Opción B: Telegram (alternativa)**
```bash
# Terminal 1
python server.py

# Terminal 2
python Telegram_bridge.py

# Envía mensajes al bot de Telegram
```

**Opción C: Script directo**
```bash
python Alex.py
```

## Ejemplo de conversación

**Tú:** "Necesito ayuda con un código Python que no funciona"

**Alex (internamente):**
1. Lee el contexto histórico (¿hemos hablado de Python antes?)
2. Razona: "Necesito entender el problema específico"
3. Decide: "Voy a usar read_file si me da la ruta"
4. Responde de forma directa y escéptica

**Alex (respuesta):**
"Dale la ruta del archivo. No me hagas adivinar. Necesito ver el código exacto y el error que tira."

---

## Ventajas de esta arquitectura

✓ Un agente, una responsabilidad (enfocado en ti)
✓ Razonamiento profundo en cada interacción
✓ Autonomía real en la ejecución
✓ Mejor integración de memoria
✓ Escala eficientemente
✓ Personalidad consistente

No es un coordinador de múltiples agentes. **Es tu agente personal.**
