"""Configuración central del proyecto.

Todas las rutas son ABSOLUTAS (derivadas de la ubicación de este fichero) para
que el servidor funcione sin importar el directorio de trabajo desde el que se
arranque. Esto corrige la fragilidad de los scripts de dia-3/dia-4, que asumían
ejecutarse desde la raíz del repo.
"""

from pathlib import Path

# Raíz del proyecto (proyecto_base/), un nivel por encima de app/
BASE_DIR = Path(__file__).resolve().parent.parent

# Modelos servidos por Ollama en http://localhost:11434
# Comprobar con `ollama list` que estén descargados antes de arrancar.
LLM_MODEL = "qwen3:8b"
EMBEDDING_MODEL = "nomic-embed-text"
TEMPERATURE = 0.3

# ChromaDB: store propio del proyecto (no se mezcla con el ./chroma_db de la raíz)
COLLECTION_NAME = "faq_python"
PERSIST_DIR = str(BASE_DIR / "chroma_db")

# Documento de preguntas frecuentes que alimenta el RAG del nivel 1
FAQ_PATH = BASE_DIR / "data" / "faq_python.md"

# Cuántos fragmentos recupera el retriever del nivel 1
TOP_K = 3
