import json
import math
import re
import sqlite3
from datetime import datetime
from typing import Optional, List
from Memory import db

STOPWORDS = {"el","la","de","que","y","a","en","un","una","es","por","con","para",
             "los","las","del","se","su","al","lo","como","pero","sus","le","ya",
             "o","fue","este","ha","esta","son","entre","cuando","muy","sin",
             "sobre","también","me","hasta","hay","donde","desde","todo","nos",
             "durante","todos","uno","les","ni","contra","otros","ese","eso",
             "ante","ellos","esto","antes","algunos","unos","yo","otro","otras",
             "otra","él","tanto","esa","estos","mucho","nada","muchos","cual",
             "poco","ella","estar","estas","algunas","algo","nosotros"}

def _tokenize(text: str) -> List[str]:
    return [w for w in re.findall(r"[a-záéíóúñü0-9]+", text.lower())
            if w not in STOPWORDS and len(w) > 2]

def _load_all_facts():
    with db.get_connection() as conn:
        return conn.execute("SELECT * FROM facts").fetchall()

def load_memories() -> List[str]:
    """Compat: lista plana de textos (usado por Memory/__init__.py)."""
    return [row["text"] for row in _load_all_facts()]

def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def _find_similar_fact(conn, text: str, threshold: float = 0.6):
    """Busca una memoria existente que hable de lo mismo (alto solape de
    palabras), para actualizarla en vez de duplicarla. Sin esto, cada
    `remember` sobre un tema ya conocido (p.ej. el estado de un proyecto)
    se apila como un hecho nuevo mientras el viejo se queda ahí para
    siempre, compitiendo por los mismos top_k resultados en las búsquedas."""
    tokens = _tokenize(text)
    if not tokens:
        return None
    best, best_score = None, threshold
    for row in conn.execute("SELECT id, text FROM facts").fetchall():
        score = _jaccard(tokens, _tokenize(row["text"]))
        if score >= best_score:
            best, best_score = row, score
    return best

def save_memory(text: str, category: Optional[str] = None, importance: int = 3) -> bool:
    text = (text or "").strip()
    if not text:
        return False
    now = datetime.now().isoformat()
    with db.get_connection() as conn:
        if conn.execute("SELECT 1 FROM facts WHERE text = ?", (text,)).fetchone():
            return False

        similar = _find_similar_fact(conn, text)
        if similar:
            conn.execute(
                "UPDATE facts SET text = ?, category = COALESCE(?, category), "
                "importance = ?, created_at = ?, access_count = 0, last_accessed_at = NULL "
                "WHERE id = ?",
                (text, category, importance, now, similar["id"])
            )
            conn.commit()
            return True

        try:
            cur = conn.execute(
                "INSERT OR IGNORE INTO facts (text, category, importance, created_at, access_count) "
                "VALUES (?, ?, ?, ?, 0)",
                (text, category, importance, now)
            )
            conn.commit()
            return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False

def _importance_recency_mult(row, now) -> float:
    importance_mult = 1.0 + (row["importance"] - 3) * 0.15
    try:
        age_days = (now - datetime.fromisoformat(row["created_at"])).days
    except Exception:
        age_days = 0
    # Vida media de ~90 días: una memoria fresca pesa el doble que una de
    # tres meses. Antes el piso era 0.7 sobre un año completo, tan plano
    # que lo viejo y lo reciente competían casi igual en el ranking.
    recency_mult = 0.5 + 0.5 * (1.0 / (1.0 + age_days / 90.0))
    return importance_mult * recency_mult

def search_memories(query: str, top_k: int = 3) -> List[str]:
    facts = _load_all_facts()
    if not facts or not query:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    docs_tokens = [_tokenize(row["text"]) for row in facts]
    N = len(facts)
    df: dict = {}
    for toks in docs_tokens:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1

    def idf(term: str) -> float:
        return math.log((N + 1) / (df.get(term, 0) + 1)) + 1

    now = datetime.now()
    scored = []
    for row, toks in zip(facts, docs_tokens):
        if not toks:
            continue
        tf: dict = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        score = sum((tf[qt] / len(toks)) * idf(qt) for qt in query_tokens if qt in tf)
        if score <= 0:
            continue

        scored.append((score * _importance_recency_mult(row, now), row))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    if top:
        now_iso = now.isoformat()
        with db.get_connection() as conn:
            conn.executemany(
                "UPDATE facts SET access_count = access_count + 1, last_accessed_at = ? WHERE id = ?",
                [(now_iso, row["id"]) for _, row in top]
            )
            conn.commit()

    return [row["text"] for _, row in top]

def get_context_for_message(user_input: str, top_k: int = 3) -> str:
    if not user_input:
        return ""
    memories = search_memories(user_input, top_k=top_k)
    if not memories:
        # TF-IDF puro no encontró coincidencia de palabras clave (p.ej.
        # preguntas meta como "¿qué recuerdas de ayer?" no comparten
        # vocabulario con los hechos guardados). Cae a los hechos más
        # importantes/recientes en vez de dejar a Alex sin memoria alguna,
        # que la llevaba a reportar "memoria vacía" cuando no lo estaba.
        facts = _load_all_facts()
        if not facts:
            return ""
        now = datetime.now()
        fallback = sorted(
            facts, key=lambda row: _importance_recency_mult(row, now), reverse=True
        )[:top_k]
        memories = [row["text"] for row in fallback]
    return "Memorias relevantes:\n" + "\n".join(f"- {m}" for m in memories)

def forget(identifier: str) -> str:
    identifier = str(identifier).strip()
    with db.get_connection() as conn:
        if identifier.isdigit():
            row = conn.execute("SELECT text FROM facts WHERE id = ?", (int(identifier),)).fetchone()
            if not row:
                return f"No existe ninguna memoria con id {identifier}."
            conn.execute("DELETE FROM facts WHERE id = ?", (int(identifier),))
            conn.commit()
            return f"Memoria olvidada: {row['text']}"

        row = conn.execute("SELECT id, text FROM facts WHERE text = ?", (identifier,)).fetchone()
        if row:
            conn.execute("DELETE FROM facts WHERE id = ?", (row["id"],))
            conn.commit()
            return f"Memoria olvidada: {row['text']}"

    candidates = search_memories(identifier, top_k=1)
    if not candidates:
        return f"No encontré ninguna memoria que coincida con: {identifier}"

    best_text = candidates[0]
    with db.get_connection() as conn:
        conn.execute("DELETE FROM facts WHERE text = ?", (best_text,))
        conn.commit()

    return f"Memoria olvidada: {best_text}"

def save_turn(channel: str, role: str, content) -> None:
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO conversation_turns (channel, role, content, created_at) VALUES (?, ?, ?, ?)",
            (channel, role, json.dumps(content, ensure_ascii=False), datetime.now().isoformat())
        )
        conn.commit()

def load_history(channel: str, limit: int = 20) -> List[dict]:
    """Carga el historial reciente. Alex es una sola entidad para Cris, así
    que el historial es compartido entre canales (web, telegram, etc.) en
    vez de aislado por canal: el parámetro `channel` solo se usa para
    etiquetar turnos nuevos en save_turn, no para filtrar la lectura."""
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content FROM conversation_turns ORDER BY id DESC LIMIT ?",
            (limit * 2,)
        ).fetchall()

    rows = list(reversed(rows))
    parsed = []
    for row in rows:
        try:
            content = json.loads(row["content"])
        except json.JSONDecodeError:
            content = row["content"]
        parsed.append({"role": row["role"], "content": content})

    window = parsed[-limit:]
    for i, turn in enumerate(window):
        if turn["role"] == "user" and isinstance(turn["content"], str):
            return window[i:]

    return []
