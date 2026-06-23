"""Configuración central del soporte Smart WiFi 6.

El proyecto usa rutas absolutas derivadas de este fichero para poder ejecutarse
desde Streamlit, desde scripts de prueba o desde cualquier terminal de clase sin
depender del directorio actual.
"""

import os
from pathlib import Path

# Raíz del proyecto y carpeta del curso.
BASE_DIR = Path(__file__).resolve().parent.parent
# Las fuentes RAG se ubican ahora en la carpeta 'data/' dentro del proyecto.
DATA_DIR = BASE_DIR / "data"

# Modelo servido por Ollama. Es pequeño para que funcione mejor en los PCs de
# clase, y todo el proyecto evita depender de embeddings externos pesados.
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemma3:4b")
TEMPERATURE = 0.2
TIMEOUT_SECONDS = 120



# Fuentes RAG separadas por nivel.
FAQ_PDF_PATH = DATA_DIR / "Las 50 preguntas más frecuentes sobre el router Smart WiFi 6 de Movistar.pdf"
MANUAL_PDF_PATH = DATA_DIR / "manual-de-configuracion-del-router-movistar_compress.pdf"

# Recuperación local. TOP_K es pequeño para mantener prompts ligeros con Gemma.
TOP_K_N1 = 4
TOP_K_N2 = 5
FAQ_CHUNK_CHARS = 1800
MANUAL_CHUNK_CHARS = 2200
CHUNK_OVERLAP = 250

# Umbrales conservadores: si no hay coincidencia léxica suficiente, el agente
# escala antes de inventar una respuesta.
N1_MIN_SCORE = 2.1
N2_MIN_SCORE = 1.6

# Contacto inventado para el último escalado.
HUMAN_PHONE = "900 123 456"
HUMAN_EMAIL = "soporte.smartwifi6@example.com"
