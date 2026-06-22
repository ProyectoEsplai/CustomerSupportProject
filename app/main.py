"""Aplicación FastAPI: chatbot de soporte de Python con recepción y escalado.

Arranque (lifespan): indexa la FAQ en ChromaDB (idempotente) y compila el grafo
una sola vez. A diferencia de dia-5, la indexación no ocurre a nivel de import.

Endpoints:
- GET  /                         → UI de chat (HTML)
- POST /chat                     → envía un mensaje y recibe respuesta
- POST /session/{id}/finalizar   → cierra la sesión (el usuario quedó a gusto)
- GET  /session/{id}             → estado e historial (depuración)
- GET  /health                   → comprobación de vida
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config, indexing, sessions
from .graph import construir_grafo
from .schemas import ChatRequest, ChatResponse, FinalizarResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proyecto_base")

# Recursos compartidos, inicializados en el lifespan.
RECURSOS: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Indexando la FAQ en ChromaDB...")
    indexing.indexar()
    logger.info("Compilando el grafo de soporte...")
    RECURSOS["grafo"] = construir_grafo()
    logger.info("Listo. Servidor preparado.")
    yield
    RECURSOS.clear()


app = FastAPI(title="Soporte Python — Chatbot con escalado", lifespan=lifespan)

app.mount(
    "/static", StaticFiles(directory=str(config.BASE_DIR / "static")), name="static"
)


@app.get("/")
def index():
    return FileResponse(str(config.BASE_DIR / "static" / "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Procesa un mensaje del usuario.

    Esta función es síncrona a propósito: ChatOllama.invoke bloquea, así que
    FastAPI la ejecuta en su threadpool sin congelar el event loop.
    """
    # 1. Crear sesión si es el primer mensaje.
    session_id = req.session_id or sessions.crear_sesion()
    sesion = sessions.get_sesion(session_id)
    if sesion is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    if not sesion["activa"]:
        raise HTTPException(status_code=409, detail="La sesión ya está finalizada")

    # 2. Feedback de insatisfacción sobre la respuesta anterior → escalar.
    if req.feedback == "insatisfecho":
        sessions.escalar(session_id, "feedback")

    # 3. Ejecutar el grafo con el nivel actual de la sesión.
    estado_inicial = {
        "pregunta": req.mensaje,
        "nivel": sesion["nivel"],
        "es_python": False,
        "contexto": [],
        "respuesta": "",
        "escalado": False,
        "motivo": sesion.get("motivo_escalado", ""),
    }
    resultado = RECURSOS["grafo"].invoke(estado_inicial)

    # 4. Si el grafo escaló (auto), persistir el nivel 2 en la sesión.
    if resultado.get("escalado") and sesion["nivel"] != 2:
        sessions.escalar(session_id, resultado.get("motivo", "auto"))

    # 5. Registrar el turno y responder.
    sessions.registrar_turno(
        session_id, req.mensaje, resultado["respuesta"], resultado["nivel"]
    )
    return ChatResponse(
        session_id=session_id,
        nivel=resultado["nivel"],
        respuesta=resultado["respuesta"],
        escalado=resultado.get("escalado", False),
        motivo=resultado.get("motivo", ""),
    )


@app.post("/session/{session_id}/finalizar", response_model=FinalizarResponse)
def finalizar(session_id: str):
    """Cierra la sesión cuando el usuario queda a gusto con las respuestas."""
    sesion = sessions.finalizar(session_id)
    if sesion is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return FinalizarResponse(
        session_id=session_id,
        mensaje="Sesión finalizada. ¡Gracias por usar el soporte!",
        turnos=len(sesion["historial"]),
    )


@app.get("/session/{session_id}")
def estado_sesion(session_id: str):
    sesion = sessions.get_sesion(session_id)
    if sesion is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return sesion
