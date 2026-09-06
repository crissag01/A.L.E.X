import requests
import re
import html

def web_search(query: str) -> str:
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        resp.raise_for_status()
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', resp.text, re.S)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', resp.text, re.S)
        results = []
        for t, s in list(zip(titles, snippets))[:5]:
            ct = html.unescape(re.sub(r"<[^<]+?>", "", t)).strip()
            cs = html.unescape(re.sub(r"<[^<]+?>", "", s)).strip()
            results.append(f"{ct}: {cs}")
        return "\n".join(results) if results else "Sin resultados."
    except Exception as e:
        return f"Error en búsqueda: {e}"
