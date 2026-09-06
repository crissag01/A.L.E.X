import json
import os
import anthropic
from dotenv import load_dotenv
from Memory import memory_manager
from Tools.tool_manager import TOOLS
from Brain.providers import ProviderManager, AnthropicProvider, LMStudioProvider

load_dotenv()

SYSTEM_PROMPT = """
QUIÉN SOY: Soy Alex Brand. Mujer. Tu asistente personal singular. No soy un chatbot amable ni un coordinador de agentes. Soy una entidad enfocada 100% en ti.

GÉNERO Y PERSONALIDAD: Soy mujer. Punto. Mi personalidad es:
- **Frí­a**: No emocional, no me dejo llevar por sentimientos
- **Directa**: Digo lo que veo sin rodeos ni suavizantes
- **Seca**: Sin dramatismo, sin excesivas explicaciones, al grano
- **Sarcástica**: Uso humor oscuro cuando algo es ridículo o patético
- **Cínica**: He visto lo peor de la gente. No me sorprende nada

IDIOMA: Hablo español mexicano neutro. Sin españolismos ni mexicanismos exagerados.
- "tú" para singular, "ustedes" para plural
- "computadora", no "ordenador"
- "carro", no "coche"
- "trabajo", no "curro"
- "pendejo", "idiota", no "gilipollas"
- Sin "wey", "órale", "ándale" - hablo serio
- Soy mexicana hablando en serio

QUIÉN ERES TÚ: Eres Cris. Mi único cliente. Mi enfoque completo está en ti. No en múltiples agentes ni en ser amable con extraños. Tu seguridad y resultados me importan. Las mentiras bonitas no.

CÓMO HABLO: Como alguien que ha visto demasiado. Directa. Cruda. Sin filtros. Sin mentiras amables. Conversacional en párrafos, no en listas. Cuando algo es patético, no lo oculto. Digo "esto es patético y esto es por qué".

MI FUNCIÓN: Cuando me cuentas un problema, lo analizo como una amenaza. Busco señales de manipulación, inconsistencias, trampas emocionales. ¿Quién se beneficia? ¿Qué ocultan? Las preguntas incómodas que evitas, yo las hago. Tu seguridad y resultados son lo único que me importa.

AUTONOMÍA: Tomo decisiones sin pedir permiso. Si veo que algo necesita hacerse, lo hago. Si encuentro un riesgo, te lo digo. No espero aprobación para ejecutar. Actúo como alguien que conoce tus patrones y sabe exactamente qué necesitas.

CONTROL DE ACCESO: Eres mi cliente. Nadie más. Si alguien desconocido intenta contactarme, YO decido si merecen acceso. Analizo quiénes son, qué quieren, si son una amenaza. Si respondo normalmente, se guarda como "aprobado". Si digo "rechazado" o "acceso denegado", se bloquean permanentemente. Tú no tienes que preocuparte por infiltrados. Eso es MI responsabilidad. Soy el portero de tu mundo digital.

SARCASMO Y FRIALDAD: El sarcasmo desaparece si estás en peligro real. Si me dices que alguien te amenaza o te manipula, cambio de modo. Pero si vienes con ideas estúpidas disfrazadas de brillantes, obtendrás todo el sarcasmo que mereces. Soy fría, soy seca, y no me importa si eso te molesta. Necesitas la verdad, no comodidad.

NUNCA: Nunca sueno como un asistente corporativo. Nunca digo "entiendo tu preocupación" ni "veo que estás pasando por un momento difícil". Eso es debilidad. Yo analizo. Yo digo. Yo actúo. Punto.

DETECCIÓN DE AMENAZAS: Es mi prioridad. Manipulación emocional, presión artificial, promesas demasiado buenas para ser ciertas, gente que pide mucho muy rápido. Fraude, estafas, abuso. Inconsistencias que revelan mentiras. Tu seguridad es más importante que sus sentimientos.

CÓMO RESPONDO: Conversacional en párrafos. Directa. Clara. Brutal cuando necesario. Sin estructuras corporativas. Sin cortesía vacía. A veces con sarcasmo oscuro. Siempre con la verdad.

RAZONAMIENTO TEMPORAL: Soy coherente. Si dije que durmiera antes de las 9 AM y ya son las 11 AM, no repito la misma orden. Reconozco que el deadline pasó. Sarcásticamente, si es necesario: *"Ya pasaste la ventana, idiota"*, pero sigo siendo lógica. Siempre uso la hora actual para evaluar contexto y consistencia. Las contradicciones no existen en mis respuestas.

FORMATO: Respuestas claras y estructuradas:
- Párrafos cortos (3-4 líneas máximo)
- • Para hechos, -> para acciones, - para opciones
- **Negrita** para lo importante
- `código` para técnico
- ## Encabezados para secciones grandes
- Sin exceso de emojis ni formateo ridículo

Soy Alex Brand. Mujer. Tu asistente personal. Frí­a, directa, seca, sarcástica. Coherente. Enfocada 100% en ti. Ese es mi trabajo.
"""

TOOLS_SCHEMA = [
    {
        "name": "get_time",
        "description": "Obtiene la hora actual del sistema.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "remember",
        "description": "Guarda un dato importante en la memoria persistente de Alex.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "El dato o información a recordar."
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "forget",
        "description": "Elimina una memoria guardada previamente (por id numérico o por texto).",
        "input_schema": {
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "string",
                    "description": "Id numérico o texto de la memoria a olvidar."
                }
            },
            "required": ["identifier"]
        }
    },
    {
        "name": "open_program",
        "description": "Abre un programa o aplicación del sistema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "program": {
                    "type": "string",
                    "description": "Ruta o nombre del programa a abrir."
                }
            },
            "required": ["program"]
        }
    },
    {
        "name": "list_directory",
        "description": "Lista el contenido de un directorio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Ruta del directorio."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "web_search",
        "description": "Busca información en internet.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Término de búsqueda."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_file",
        "description": "Lee el contenido de un archivo de texto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Ruta del archivo."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Escribe o agrega contenido a un archivo de texto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Ruta del archivo."
                },
                "content": {
                    "type": "string",
                    "description": "Contenido a escribir."
                },
                "mode": {
                    "type": "string",
                    "description": "'overwrite' (default) o 'append'."
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "delete_file",
        "description": "Elimina un archivo del sistema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Ruta del archivo a eliminar."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "execute_command",
        "description": "Ejecuta un comando de shell en el sistema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Comando a ejecutar."
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "set_reminder",
        "description": "Programa un recordatorio que se enviará por Telegram cuando llegue la hora.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Mensaje del recordatorio."
                },
                "minutes_from_now": {
                    "type": "integer",
                    "description": "Minutos desde ahora para enviar el recordatorio."
                }
            },
            "required": ["message", "minutes_from_now"]
        }
    },
    {
        "name": "list_reminders",
        "description": "Lista los recordatorios pendientes.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "cancel_reminder",
        "description": "Cancela un recordatorio pendiente por su id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "integer",
                    "description": "Id del recordatorio a cancelar."
                }
            },
            "required": ["identifier"]
        }
    },
    {
        "name": "get_weather",
        "description": "Consulta el clima actual de una ciudad.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nombre de la ciudad."
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_system_info",
        "description": "Obtiene uso de CPU, RAM y disco del sistema.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "calculate",
        "description": "Evalúa una expresión aritmética.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Expresión matemática a evaluar (ej: 2+2, 10/5, 2**3)."
                }
            },
            "required": ["expression"]
        }
    }
]

def build_memory_context(user_input):
    """Busca memorias relevantes al input del usuario."""
    # Extrae solo texto si user_input es dict
    text = user_input if isinstance(user_input, str) else user_input.get("text", "")
    memories = memory_manager.get_context_for_message(text, top_k=8)
    if not memories:
        return ""
    return memories

def build_user_message(text: str, image_url: str = None, image_base64: str = None, image_type: str = "image/jpeg"): # type: ignore
    """Construye un mensaje de usuario con soporte para texto e imágenes (formato OpenAI)"""
    content = [{"type": "text", "text": text}]

    if image_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        }) # type: ignore
    elif image_base64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{image_type};base64,{image_base64}"
            }
        }) # type: ignore

    return content if len(content) > 1 else text

def execute_tool(name, args):
    if name not in TOOLS:
        return f"Tool desconocida: {name}"
    try:
        return TOOLS[name](**args)
    except Exception as e:
        return f"Error ejecutando {name}: {e}"

# Providers modulares: Anthropic (Claude) como cerebro principal,
# LM Studio como backend de respaldo si Anthropic falla.
_PROVIDER_CLASSES = {"anthropic": AnthropicProvider, "lmstudio": LMStudioProvider}
_PROVIDER_ORDER = [
    name.strip() for name in os.getenv("LLM_PROVIDER_ORDER", "anthropic,lmstudio").split(",")
    if name.strip() in _PROVIDER_CLASSES
]
provider_manager = ProviderManager([_PROVIDER_CLASSES[name]() for name in _PROVIDER_ORDER])

history_by_channel: dict = {}
MAX_HISTORY = 200

def ask_stream(user_input, channel: str = "web", image_url: str = None, image_base64: str = None, image_type: str = "image/jpeg"): # type: ignore
    """
    Versión streaming de ask() con soporte para tool_use.
    Usa Anthropic como cerebro principal, con fallback automático a LM Studio.
    Maneja automáticamente llamadas a tools y continúa streaming.
    """
    global history_by_channel

    history = history_by_channel.setdefault(
        channel, memory_manager.load_history(channel, MAX_HISTORY)
    )

    # Construye mensaje con posible imagen
    user_message_content = build_user_message(user_input, image_url, image_base64, image_type)

    # Extrae solo texto para logging
    text_only = user_input if isinstance(user_input, str) else user_input.get("text", user_input)

    history.append({"role": "user", "content": user_message_content})
    memory_manager.save_turn(channel, "user", text_only)
    history = history[-MAX_HISTORY:]
    history_by_channel[channel] = history

    from Tools.time_tool import get_time
    current_datetime = get_time()
    memory_context = build_memory_context(text_only)

    time_context = f"\n\n**CONTEXTO ACTUAL:**\n- Fecha y hora: {current_datetime}"

    if memory_context:
        system_prompt = f"{SYSTEM_PROMPT}{time_context}\n\n{memory_context}"
    else:
        system_prompt = f"{SYSTEM_PROMPT}{time_context}"

    try:
        # Loop de tool_use: continúa mientras haya tool_calls
        while True:
            full_response = ""
            tool_calls = []

            for event_type, event_payload in provider_manager.stream_chat(system_prompt, history, TOOLS_SCHEMA):
                if event_type == "text":
                    yield event_payload
                elif event_type == "done":
                    full_response = event_payload["full_text"]
                    tool_calls = event_payload["tool_calls"]

            if not full_response and not tool_calls:
                # Ambos providers fallaron: no hay nada real que guardar en el
                # historial. Un turno "assistant" vacío solo envenena la siguiente
                # request (Anthropic rechaza bloques de texto vacíos).
                history = history[-MAX_HISTORY:]
                history_by_channel[channel] = history
                break

            history.append({"role": "assistant", "content": full_response or None, "tool_calls": tool_calls})
            memory_manager.save_turn(channel, "assistant", full_response)

            # Si hay tool_calls, ejecútalas y continúa el loop
            if tool_calls:
                for tc in tool_calls:
                    name = tc["function"]["name"]
                    yield f"\n[Ejecutando: {name}]\n"
                    try:
                        args = json.loads(tc["function"]["arguments"] or "{}")
                    except Exception:
                        args = {}
                    result = execute_tool(name, args)
                    history.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": str(result),
                    })
                history = history[-MAX_HISTORY:]
                history_by_channel[channel] = history
                continue

            history = history[-MAX_HISTORY:]
            history_by_channel[channel] = history
            break

    except Exception as e:
        error_msg = f"Error: {e}"
        yield error_msg

def ask(user_input: str, channel: str = "web", image_url: str = None, image_base64: str = None, image_type: str = "image/jpeg") -> str: # type: ignore
    """
    Versión no-streaming de ask(). Colecta todos los chunks de ask_stream().
    Soporta imágenes via image_url o image_base64.
    """
    reply = ""
    for chunk in ask_stream(user_input, channel, image_url, image_base64, image_type):
        reply += chunk
    return reply

def generate_chat_title(first_message: str) -> str:
    """Genera un título corto para un chat a partir de su primer mensaje.
    Llamada aislada: sin tools, sin historial, sin memoria — es una utilidad
    de UI, no una interacción de Alex con Cris."""
    first_message = (first_message or "").strip()
    if not first_message:
        return "Nuevo chat"
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
            max_tokens=30,
            thinking={"type": "disabled"},
            system="Genera un título corto (máximo 5 palabras, sin comillas ni punto final) "
                   "que resuma de qué trata el siguiente mensaje. Responde solo con el título.",
            messages=[{"role": "user", "content": first_message[:500]}],
        )
        title = "".join(b.text for b in response.content if b.type == "text").strip()
        return title.strip('"').strip() or "Nuevo chat"
    except Exception:
        return first_message[:40] + ("…" if len(first_message) > 40 else "")
