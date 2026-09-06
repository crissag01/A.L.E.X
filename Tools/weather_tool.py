import requests

def get_weather(city: str) -> str:
    try:
        resp = requests.get(f"https://wttr.in/{city}", params={"format": "3"}, timeout=10)
        resp.raise_for_status()
        return resp.text.strip()
    except Exception as e:
        return f"Error obteniendo clima: {e}"
