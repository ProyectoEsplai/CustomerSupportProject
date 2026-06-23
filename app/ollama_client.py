"""Cliente mínimo para Ollama usando solo la librería estándar."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from . import config


class OllamaError(RuntimeError):
    """Error controlado para mostrar mensajes claros en Streamlit."""


def generar_respuesta(
    mensajes: list[dict[str, str]],
    *,
    modelo: str = config.LLM_MODEL,
    temperatura: float = config.TEMPERATURE,
    timeout: int = config.TIMEOUT_SECONDS,
) -> str:
    payload = {
        "model": modelo,
        "messages": mensajes,
        "stream": False,
        "options": {
            "temperature": temperatura,
            "num_predict": 700,
        },
    }
    data = _post_json("/api/chat", payload, timeout=timeout)
    contenido = data.get("message", {}).get("content", "")
    if not contenido:
        raise OllamaError("Ollama no devolvió contenido para la respuesta.")
    return _limpiar_salida_modelo(contenido)


def estado_ollama() -> dict[str, object]:
    """Devuelve estado de conexión y modelos disponibles."""
    try:
        data = _get_json("/api/tags", timeout=8)
    except OllamaError as exc:
        return {"ok": False, "modelos": [], "mensaje": str(exc)}

    modelos = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    disponible = config.LLM_MODEL in modelos
    mensaje = (
        f"Modelo {config.LLM_MODEL} disponible."
        if disponible
        else f"Ollama responde, pero no aparece {config.LLM_MODEL}."
    )
    return {"ok": disponible, "modelos": modelos, "mensaje": mensaje}


def _post_json(path: str, payload: dict, timeout: int) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{config.OLLAMA_BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaError(
            f"No puedo conectar con Ollama en {config.OLLAMA_BASE_URL}. "
            "Comprueba que Ollama esté abierto y que el modelo esté descargado."
        ) from exc
    except json.JSONDecodeError as exc:
        raise OllamaError("Ollama devolvió una respuesta no válida.") from exc


def _get_json(path: str, timeout: int) -> dict:
    try:
        with urllib.request.urlopen(f"{config.OLLAMA_BASE_URL}{path}", timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaError(
            f"No puedo conectar con Ollama en {config.OLLAMA_BASE_URL}."
        ) from exc
    except json.JSONDecodeError as exc:
        raise OllamaError("Ollama devolvió una respuesta no válida.") from exc


def _limpiar_salida_modelo(texto: str) -> str:
    texto = texto.strip()
    if "</think>" in texto:
        texto = texto.split("</think>", 1)[1].strip()
    return texto
