"""Modelos Pydantic para la API de chat."""

from typing import Literal, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    mensaje: str
    session_id: Optional[str] = None
    # Feedback sobre la respuesta ANTERIOR: si es "insatisfecho" la sesión
    # escala a nivel 2 antes de responder este mensaje.
    feedback: Optional[Literal["satisfecho", "insatisfecho"]] = None


class ChatResponse(BaseModel):
    session_id: str
    nivel: int
    respuesta: str
    escalado: bool
    motivo: str


class FinalizarResponse(BaseModel):
    session_id: str
    mensaje: str
    turnos: int
