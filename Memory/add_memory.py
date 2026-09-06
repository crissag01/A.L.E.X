import chromadb
from chromadb.utils import embedding_functions
import os

# 1. Crear cliente local (persistencia en carpeta "chroma_data")
client = chromadb.PersistentClient(path="/C:/Users/Cris/Downloads/Alex v1 (Stable)/Memory/")

# 2. Definir función de embeddings (aquí un ejemplo simple con texto plano)
#    Puedes usar modelos más avanzados como OpenAI, HuggingFace, etc.
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # Modelo rápido y ligero
)

# 3. Crear o recuperar colección
collection = client.get_or_create_collection(
    name="Cris_collection",
    embedding_function=embedding_fn # type: ignore
)

# 4. Insertar documentos
collection.add(
    documents=[
        "Nombre: Cristofer, Edad: 19 años, Profesión: Freelancer.",
        "Persoanalidad: Introvertido, Sarcastico",
        "Intereses: Programación, Inteligencia Artificial, Videojuegos, Música."
    ],
    ids=["A1", "A2", "A3"]
)

# 5. Consulta por similitud
query = "¿Quien es Cristofer?"
results = collection.query(
    query_texts=[query],
    n_results=3
)

print("Resultados de la búsqueda:")
for doc, score in zip(results["documents"][0], results["distances"][0]): # type: ignore
    print(f"- {doc} (distancia: {score:.4f})")
