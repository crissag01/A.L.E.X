import requests
import time
import os
from dotenv import load_dotenv
from Brain.brain import ask
from Memory import db as memory_db
from Memory import reminder_manager
from Tools.telegram_commands import handle_command
from Tools.access_control import check_access, needs_alex_decision, approve_user, reject_user, get_access_decision_prompt

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID")) # type: ignore
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

last_update_id = 0

def get_updates():
    global last_update_id
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 30}

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["ok"]:
            for update in data["result"]:
                last_update_id = max(last_update_id, update["update_id"])
                process_message(update)
    except Exception as e:
        print(f"❌ Error obteniendo updates: {e}")

def process_message(update):
    if "message" not in update:
        return

    message = update["message"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    username = message["from"].get("username", f"user_{user_id}")
    text = message.get("text", "")

    if not text:
        return

    # Control de acceso
    allowed, status = check_access(user_id)

    if status == "rejected":
        print(f"🚫 Usuario rechazado: {username} ({user_id})")
        return

    if status == "new":
        print(f"🤔 Usuario nuevo requiere aprobación: {username} ({user_id})")
        # Alex decide si permitir acceso
        decision_prompt = get_access_decision_prompt(user_id, username, text)
        combined_input = decision_prompt + "\n" + text
        send_typing_action(chat_id)
        reply = ask(combined_input, channel="telegram")

        # Registrar la decisión basada en la respuesta de Alex
        if any(palabra in reply.lower() for palabra in ["rechazad", "acceso denegad", "no permito", "bloqueado"]):
            reject_user(user_id, username, "Auto-rechazado por Alex")
            print(f"❌ Alex rechazó a {username}")
        else:
            approve_user(user_id, username, "Auto-aprobado por Alex")
            print(f"✅ Alex aprobó a {username}")

        send_message(chat_id, reply)
        return

    # Usuario aprobado u owner
    memory_db.set_state("telegram_last_chat_id", str(chat_id))

    if text.startswith("/"):
        handle_command(text, chat_id, send_message)
        return

    print(f"📨 Mensaje recibido: {text[:120]}...")
    send_typing_action(chat_id)
    reply = ask(text, channel="telegram")
    send_message(chat_id, reply)

def send_typing_action(chat_id):
    url = f"{BASE_URL}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"⚠️ Error enviando acción de typing: {e}")

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"

    if len(text) > 4096:
        chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for chunk in chunks:
            payload = {"chat_id": chat_id, "text": chunk}
            try:
                requests.post(url, json=payload)
            except Exception as e:
                print(f"❌ Error enviando mensaje: {e}")
    else:
        payload = {"chat_id": chat_id, "text": text}
        try:
            requests.post(url, json=payload)
            print(f"✅ Respuesta enviada")
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")

def check_reminders():
    due = reminder_manager.get_due_reminders()
    if not due:
        return
    chat_id = memory_db.get_state("telegram_last_chat_id")
    if not chat_id:
        print("⚠️ Recordatorio(s) pendiente(s) pero aún no se conoce un chat_id.")
        return
    for r in due:
        send_message(int(chat_id), f"⏰ Recordatorio: {r['message']}")
        reminder_manager.mark_sent(r["id"])

def start_polling():
    print("🔄 Telegram Bridge iniciado")
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

if __name__ == "__main__":
    start_polling()
