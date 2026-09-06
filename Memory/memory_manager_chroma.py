import chromadb
import json
import os
from datetime import datetime

# Inicializar ChromaDB
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_data")
try:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name="alex_memories",
        metadata={"hnsw:space": "cosine"}
    )
    CHROMA_AVAILABLE = True
except Exception as e:
    print(f"ChromaDB error: {e}. Usando fallback JSON.")
    client = None
    collection = None
    CHROMA_AVAILABLE = False

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")

def load_memory_data():
    """Carga datos del JSON (para compatibilidad)."""
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def load_memories():
    """Carga todas las memorias desde ChromaDB."""
    try:
        results = collection.get()
        if not results["ids"]:
            return []
        return results["documents"]
    except Exception as e:
        print(f"Error cargando memorias: {e}")
        return []

def search_memories(query, top_k=5):
    """Busca memorias similares a una query usando embeddings (o búsqueda simple)."""
    if not CHROMA_AVAILABLE or not collection:
        # Fallback: búsqueda simple basada en palabras clave
        all_memories = load_memories()
        query_words = query.lower().split()
        scored = []
        for mem in all_memories:
            score = sum(1 for word in query_words if word in mem.lower())
            if score > 0:
                scored.append((score, mem))
        scored.sort(reverse=True)
        return [mem for _, mem in scored[:top_k]]

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        if not results["ids"] or not results["ids"][0]:
            return []
        return results["documents"][0]
    except Exception as e:
        # Fallback a búsqueda simple
        return search_memories(query, top_k) if CHROMA_AVAILABLE else []

def save_memory(memory_text):
    """Guarda una nueva memoria en ChromaDB (o JSON si falla)."""
    # Siempre guardar en JSON
    data = load_memory_data()
    memories = data.get("memories", [])
    if memory_text not in memories:
        memories.append(memory_text)
        data["memories"] = memories
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando en JSON: {e}")
            return False

    # Intentar guardar en ChromaDB también
    if CHROMA_AVAILABLE and collection:
        try:
            memory_id = f"memory_{datetime.now().timestamp()}"
            collection.add(
                ids=[memory_id],
                documents=[memory_text],
                metadatas=[{"timestamp": datetime.now().isoformat(), "user": "criss"}]
            )
        except Exception as e:
            # Fallback OK, está guardado en JSON
            pass

    return True

def get_context_for_message(user_input, top_k=3):
    """Obtiene memorias relevantes para el contexto actual."""
    if not user_input:
        return ""

    relevant_memories = search_memories(user_input, top_k=top_k)
    if not relevant_memories:
        return ""

    return "\n".join(f"- {m}" for m in relevant_memories)
