"""Almacén opcional de sesiones de chat en memoria.

Streamlit ya mantiene el historial en `st.session_state`, pero este módulo se
conserva por si se quiere reutilizar el flujo desde una API o desde consola.
"""

import uuid
from typing import Optional

# session_id -> datos de la sesión
SESIONES: dict[str, dict] = {}


def crear_sesion() -> str:
    """Crea una sesión nueva y devuelve su identificador."""
    session_id = uuid.uuid4().hex
    SESIONES[session_id] = {
        "nivel": 1,
        "historial": [],  # lista de turnos {pregunta, respuesta, nivel}
        "activa": True,
    }
    return session_id


def get_sesion(session_id: str) -> Optional[dict]:
    return SESIONES.get(session_id)


def escalar(session_id: str, motivo: str) -> None:
    """Sube la sesión a nivel 2 (por feedback del usuario o decisión del agente)."""
    sesion = SESIONES.get(session_id)
    if sesion is not None:
        sesion["nivel"] = 2
        sesion["motivo_escalado"] = motivo


def registrar_turno(session_id: str, pregunta: str, respuesta: str, nivel: int) -> None:
    sesion = SESIONES.get(session_id)
    if sesion is not None:
        sesion["historial"].append(
            {"pregunta": pregunta, "respuesta": respuesta, "nivel": nivel}
        )


def finalizar(session_id: str) -> Optional[dict]:
    """Cierra la sesión (el usuario quedó a gusto) y devuelve sus datos."""
    sesion = SESIONES.get(session_id)
    if sesion is not None:
        sesion["activa"] = False
    return sesion
