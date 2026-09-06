from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import threading
import os
from concurrent.futures import ThreadPoolExecutor

from Brain.brain import ask, ask_stream, generate_chat_title
from Memory.memory_manager import search_memories
from Tools.telegram_commands import handle_command
from Tools.telegram_media import download_image_as_base64, download_file, extract_text_from_file
from Tools.access_control import check_access, needs_alex_decision, approve_user, reject_user, get_access_decision_prompt

# Telegram polling
telegram_thread = None

def start_telegram_polling():
    """Inicia polling de Telegram en background (no bloqueante)"""
    import requests
    import time
    import os
    from dotenv import load_dotenv
    from Memory import db as memory_db
    from Memory import reminder_manager

    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID")) # type: ignore
    BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    last_update_id = 0

    # Pool de threads para procesar mensajes sin bloquear polling
    executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="tg_worker")

    def get_updates():
        nonlocal last_update_id
        url = f"{BASE_URL}/getUpdates"
        params = {"offset": last_update_id + 1, "timeout": 30}
        try:
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            if data["ok"]:
                for update in data["result"]:
                    last_update_id = max(last_update_id, update["update_id"])
                    # Procesa en thread separado para no bloquear polling
                    executor.submit(process_message, update)
        except Exception as e:
            print(f"Error obteniendo updates: {e}")

    def stream_reply_to_telegram(chat_id, gen):
        """
        Consume un generador de ask_stream y lo refleja en Telegram:
        - Mantiene viva la animación nativa de "escribiendo" durante toda la espera
          (incluida la fase de extended thinking, donde no llega texto todavía).
        - Edita el mensaje por tiempo transcurrido, no por conteo de chunks, para no
          chocar con el rate limit de editMessageText de Telegram.
        Devuelve el texto acumulado final.
        """
        EDIT_INTERVAL = 1.2  # segundos entre ediciones
        TYPING_REFRESH = 4   # el "escribiendo" de Telegram expira ~5s

        stop_typing = threading.Event()

        def typing_loop():
            while not stop_typing.is_set():
                send_typing_action(chat_id)
                stop_typing.wait(TYPING_REFRESH)

        typing_thread = threading.Thread(target=typing_loop, daemon=True)
        typing_thread.start()

        initial_msg = requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": chat_id, "text": "escribiendo..."}
        ).json()
        message_id = initial_msg.get("result", {}).get("message_id")

        accumulated = ""
        last_edit = 0.0

        try:
            for chunk in gen:
                accumulated += chunk
                now = time.monotonic()
                if message_id and (now - last_edit) >= EDIT_INTERVAL:
                    try:
                        requests.post(
                            f"{BASE_URL}/editMessageText",
                            json={
                                "chat_id": chat_id,
                                "message_id": message_id,
                                "text": accumulated if accumulated else "escribiendo...",
                                "parse_mode": "Markdown"
                            }
                        )
                        last_edit = now
                    except:
                        pass
        except Exception as e:
            accumulated = f"Error: {e}"
        finally:
            stop_typing.set()

        if message_id:
            try:
                requests.post(
                    f"{BASE_URL}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": accumulated or "...",
                        "parse_mode": "Markdown"
                    }
                )
            except:
                send_message(chat_id, accumulated)
        else:
            send_message(chat_id, accumulated)

        return accumulated

    def process_message(update):
        if "message" not in update:
            return
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username", f"user_{user_id}")
        text = message.get("text", "")

        # Control de acceso
        allowed, status = check_access(user_id)

        if status == "rejected":
            print(f"🚫 Usuario rechazado: {username} ({user_id})")
            return

        # Si es usuario nuevo, Alex decide
        if status == "new":
            print(f"🤔 Usuario nuevo requiere aprobación: {username} ({user_id})")
            if text:
                decision_prompt = get_access_decision_prompt(user_id, username, text)
                combined_input = decision_prompt + "\n" + text

                accumulated = stream_reply_to_telegram(
                    chat_id, ask_stream(combined_input, channel="telegram")  # type: ignore
                )

                # Registrar decisión
                if any(palabra in accumulated.lower() for palabra in ["rechazad", "acceso denegad", "no permito", "bloqueado"]):
                    reject_user(user_id, username, "Auto-rechazado por Alex")
                    print(f"❌ Alex rechazó a {username}")
                else:
                    approve_user(user_id, username, "Auto-aprobado por Alex")
                    print(f"✅ Alex aprobó a {username}")
            return

        memory_db.set_state("telegram_last_chat_id", str(chat_id))

        # Procesar comandos
        if text and text.startswith("/"):
            handle_command(text, chat_id, send_message)
            return

        # Procesar imagen + texto
        image_base64 = None
        image_type = None
        extra_text = ""

        if "photo" in message:
            photo = message["photo"][-1]  # Última foto (más alta resolución)
            image_base64, image_type = download_image_as_base64(photo["file_id"])
            if image_base64:
                print(f"📷 Imagen recibida, resolviendo...")

        # Procesar documento
        if "document" in message:
            doc = message["document"]
            filename = download_file(doc["file_id"], doc.get("file_name"))
            if filename:
                extracted = extract_text_from_file(filename)
                if extracted:
                    extra_text = f"\n[Contenido del archivo '{doc.get('file_name', 'documento')}']:\n{extracted}"
                try:
                    os.remove(filename)
                except:
                    pass

        # Si no hay texto ni imagen, ignorar
        if not text and not image_base64 and not extra_text:
            return

        # Combina texto + contenido extraído
        full_text = (text or "") + extra_text
        if not full_text.strip():
            full_text = "[Imagen sin descripción]"

        print(f"📨 Mensaje Telegram: {full_text[:120]}...")

        accumulated = stream_reply_to_telegram(
            chat_id,
            ask_stream(full_text, channel="telegram", image_base64=image_base64, image_type=image_type)  # type: ignore
        )

    def send_typing_action(chat_id):
        url = f"{BASE_URL}/sendChatAction"
        payload = {"chat_id": chat_id, "action": "typing"}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"⚠️ Error enviando typing: {e}")

    def send_message(chat_id, text, parse_mode="Markdown"):
        url = f"{BASE_URL}/sendMessage"
        if len(text) > 4096:
            chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
            for chunk in chunks:
                payload = {"chat_id": chat_id, "text": chunk, "parse_mode": parse_mode}
                try:
                    requests.post(url, json=payload)
                except Exception as e:
                    print(f"Error enviando mensaje: {e}")
        else:
            payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
            try:
                requests.post(url, json=payload)
                print(f"Respuesta Telegram enviada")
            except Exception as e:
                print(f"Error enviando mensaje: {e}")

    def check_reminders():
        due = reminder_manager.get_due_reminders()
        if not due:
            return
        chat_id = memory_db.get_state("telegram_last_chat_id")
        if not chat_id:
            return
        for r in due:
            send_message(int(chat_id), f"⏰ Recordatorio: {r['message']}")
            reminder_manager.mark_sent(r["id"])

    print("🔄 Telegram Bridge iniciado (integrado en FastAPI)")
    print(f"👤 Escuchando mensajes de usuario {TELEGRAM_USER_ID}")
    print("🤖 Conectado a Alex (Claude Sonnet 5)")

    while True:
        try:
            get_updates()
        except Exception as e:
            print(f"⚠️ Error en polling: {e}")
            time.sleep(5)
        try:
            check_reminders()
        except Exception as e:
            print(f"⚠️ Error revisando recordatorios: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: startup y shutdown"""
    global telegram_thread
    # Startup: inicia Telegram polling en background
    telegram_thread = threading.Thread(target=start_telegram_polling, daemon=True)
    telegram_thread.start()
    yield
    # Shutdown (opcional): aquí podrías hacer cleanup si es necesario

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

class RenameRequest(BaseModel):
    name: str

class AutonameRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(msg: Message):
    reply = ask(msg.text, channel="web")
    memories = search_memories(msg.text, top_k=2)

    return {
        "reply": reply,
        "memories": memories
    }

@app.get("/resources")
def resources():
    import psutil
    cpu = psutil.cpu_percent()
    ram_used = psutil.virtual_memory().used / (1024 ** 3)
    ram_total = psutil.virtual_memory().total / (1024 ** 3)
    return {
        "cpu": int(cpu),
        "ram": f"{ram_used:.1f} / {ram_total:.1f} GB",
        "model": "claude-sonnet-5",
        "connected": True
    }

import json

CHATS_FILE = "chats.json"

def load_chats():
    if not os.path.exists(CHATS_FILE):
        return {}
    try:
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(CHATS_FILE, "r", encoding="latin-1") as f:
            return json.load(f)

def save_chats(data):
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.get("/chats")
def get_chats():
    return load_chats()

@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    chats = load_chats()
    chat = chats.get(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    return chat

@app.post("/chats/autoname")
def autoname_chat(body: AutonameRequest):
    # Declarado antes de /chats/{chat_id}: si no, FastAPI matchea
    # "autoname" como si fuera un chat_id literal.
    return {"name": generate_chat_title(body.message)}

@app.post("/chats/{chat_id}")
def save_chat(chat_id: str, body: dict):
    chats = load_chats()
    chats[chat_id] = body
    save_chats(chats)
    return {"ok": True}

@app.patch("/chats/{chat_id}/name")
def rename_chat(chat_id: str, body: RenameRequest):
    chats = load_chats()
    chat = chats.get(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    chat["name"] = body.name
    chats[chat_id] = chat
    save_chats(chats)
    return {"ok": True, "name": body.name}

# --- Frontend estático (build de producción) ---
DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")
if os.path.isdir(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")