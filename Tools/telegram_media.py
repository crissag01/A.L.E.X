"""Manejo de imágenes y archivos desde Telegram"""
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def get_file_url(file_id: str) -> str:
    """Obtiene la URL de descarga de un archivo de Telegram"""
    try:
        url = f"{BASE_URL}/getFile"
        params = {"file_id": file_id}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("ok"):
            file_path = data["result"]["file_path"]
            return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    except requests.Timeout:
        print(f"Timeout obteniendo URL de archivo (>5s)")
    except Exception as e:
        print(f"Error obteniendo URL de archivo: {e}")
    return None


def download_image_as_base64(file_id: str) -> tuple:
    """Descarga una imagen de Telegram y la convierte a base64 (con timeout)"""
    try:
        file_url = get_file_url(file_id)
        if not file_url:
            return None, None

        # Timeout más bajo para no bloquear procesamiento
        response = requests.get(file_url, timeout=10)
        if response.status_code == 200:
            base64_data = base64.b64encode(response.content).decode("utf-8")

            # Intenta detectar el tipo de imagen por extensión o header
            content_type = response.headers.get("content-type", "image/jpeg")
            if "png" in content_type.lower():
                media_type = "image/png"
            elif "gif" in content_type.lower():
                media_type = "image/gif"
            elif "webp" in content_type.lower():
                media_type = "image/webp"
            else:
                media_type = "image/jpeg"

            return base64_data, media_type
    except requests.Timeout:
        print(f"Timeout descargando imagen (>10s), descartando")
    except Exception as e:
        print(f"Error descargando imagen: {e}")
    return None, None


def download_file(file_id: str, filename: str = None) -> str:
    """Descarga un archivo de Telegram y lo guarda localmente"""
    try:
        file_url = get_file_url(file_id)
        if not file_url:
            return None

        response = requests.get(file_url)
        if response.status_code == 200:
            if not filename:
                filename = f"telegram_file_{file_id[:10]}.bin"

            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"Error descargando archivo: {e}")
    return None


def extract_text_from_file(filename: str) -> str:
    """Extrae texto de un archivo (txt, md, etc)"""
    try:
        if filename.endswith((".txt", ".md")):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        # Para PDF, necesitaría pdfplumber (dependencia adicional)
        # Por ahora, solo archivos de texto
    except Exception as e:
        print(f"Error extrayendo texto: {e}")
    return None
