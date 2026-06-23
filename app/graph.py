"""Grafo de soporte N1/N2/Humano para el Router Smart WiFi 6.

El diseño sigue el esquema del curso: el estado viaja por nodos, cada nodo añade
su resultado y los clasificadores deciden si terminar o escalar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from . import config
from .documents import (
    ResultadoBusqueda,
    cargar_corpus,
    contexto_para_prompt,
    fuentes_resumidas,
)
from .ollama_client import generar_respuesta


MARCA_ESCALAR_N2 = "ESCALAR_N2"
MARCA_ESCALAR_HUMANO = "ESCALAR_HUMANO"
TERMINOS_GENERICOS = {
    "internet",
    "movistar",
    "precio",
    "precios",
    "router",
    "smart",
    "tipo",
    "wifi",
}

EstadoPaso = Literal["pendiente", "completado", "escalado", "omitido", "final"]
TipoPaso = Literal["entrada", "rag", "agente", "clasificador", "humano", "fin"]


@dataclass
class PasoRecorrido:
    id: str
    nombre: str
    tipo: TipoPaso
    estado: EstadoPaso
    detalle: str
    fuentes: list[str] = field(default_factory=list)


@dataclass
class RespuestaSoporte:
    respuesta: str
    nivel: str
    destino: Literal["fin", "n2", "humano"]
    escalado: bool
    motivo: str
    pasos: list[PasoRecorrido]
    fuentes: list[str]
    confianza_n1: float = 0.0
    confianza_n2: float = 0.0


def procesar_consulta(pregunta: str) -> RespuestaSoporte:
    pregunta = pregunta.strip()
    if not pregunta:
        return _respuesta_vacia()

    pasos: list[PasoRecorrido] = []

    pasos.append(
        PasoRecorrido(
            id="entrada_llm",
            nombre="Entrada LLM",
            tipo="entrada",
            estado="completado",
            detalle="La consulta entra al flujo y se entrega a Soporte N1.",
        )
    )

    resultados_n1 = _rag_n1(pregunta)
    confianza_n1 = resultados_n1[0].score if resultados_n1 else 0.0
    pasos.append(
        PasoRecorrido(
            id="rag_n1",
            nombre="RAG N1",
            tipo="rag",
            estado="completado" if resultados_n1 else "escalado",
            detalle=_detalle_rag(resultados_n1, config.N1_MIN_SCORE),
            fuentes=fuentes_resumidas(resultados_n1),
        )
    )

    respuesta_n1 = _soporte_n1(pregunta, resultados_n1, confianza_n1)
    pasos.append(
        PasoRecorrido(
            id="soporte_n1",
            nombre="Soporte N1",
            tipo="agente",
            estado="escalado" if _pide_escalar_n2(respuesta_n1) else "final",
            detalle=(
                "N1 solo usa preguntas frecuentes. "
                + (
                    "No tiene una respuesta segura."
                    if _pide_escalar_n2(respuesta_n1)
                    else "Responde con la FAQ."
                )
            ),
            fuentes=fuentes_resumidas(resultados_n1),
        )
    )

    if not _pide_escalar_n2(respuesta_n1):
        pasos.append(
            PasoRecorrido(
                id="clasificador_n1",
                nombre="Clasificador N1",
                tipo="clasificador",
                estado="final",
                detalle="La respuesta de N1 es suficiente. El flujo termina.",
            )
        )
        return RespuestaSoporte(
            respuesta=respuesta_n1.strip(),
            nivel="N1",
            destino="fin",
            escalado=False,
            motivo="FAQ suficiente",
            pasos=pasos,
            fuentes=fuentes_resumidas(resultados_n1),
            confianza_n1=confianza_n1,
        )

    pasos.append(
        PasoRecorrido(
            id="clasificador_n1",
            nombre="Clasificador N1",
            tipo="clasificador",
            estado="escalado",
            detalle="La consulta requiere manual técnico. Se escala a N2.",
        )
    )
    return _resolver_n2(pregunta, pasos, confianza_n1)


def procesar_consulta_n2(pregunta: str) -> RespuestaSoporte:
    """Revisa directamente en N2 una pregunta que N1 no dejó resuelta."""
    pregunta = pregunta.strip()
    if not pregunta:
        return _respuesta_vacia()

    pasos: list[PasoRecorrido] = [
        PasoRecorrido(
            id="entrada_llm",
            nombre="Entrada LLM",
            tipo="entrada",
            estado="completado",
            detalle="La consulta se revisa de nuevo en soporte técnico N2.",
        ),
        PasoRecorrido(
            id="clasificador_n1",
            nombre="Clasificador N1",
            tipo="clasificador",
            estado="escalado",
            detalle="El usuario indica que la respuesta de N1 no solucionó la consulta.",
        ),
    ]

    resultado = _resolver_n2(pregunta, pasos, confianza_n1=0.0)
    resultado.motivo = "El usuario indicó que N1 no solucionó la consulta"
    return resultado


def escalar_a_humano(pregunta: str, motivo: str = "El usuario solicita atención humana") -> RespuestaSoporte:
    pregunta = pregunta.strip()
    pasos = [
        PasoRecorrido(
            id="entrada_llm",
            nombre="Entrada LLM",
            tipo="entrada",
            estado="completado",
            detalle="La consulta queda preparada para atención humana.",
        ),
        PasoRecorrido(
            id="humano",
            nombre="Asistente Humano",
            tipo="humano",
            estado="final",
            detalle=f"Teléfono {config.HUMAN_PHONE} · {config.HUMAN_EMAIL}",
        ),
    ]
    return RespuestaSoporte(
        respuesta=_respuesta_humano(pregunta),
        nivel="Humano",
        destino="humano",
        escalado=True,
        motivo=motivo,
        pasos=pasos,
        fuentes=[],
    )


def construir_grafo():
    """Compatibilidad con el proyecto anterior: devuelve el procesador callable."""
    return procesar_consulta


def _resolver_n2(
    pregunta: str, pasos: list[PasoRecorrido], confianza_n1: float
) -> RespuestaSoporte:
    resultados_n2 = _rag_n2(pregunta)
    confianza_n2 = resultados_n2[0].score if resultados_n2 else 0.0
    pasos.append(
        PasoRecorrido(
            id="rag_n2",
            nombre="RAG N2",
            tipo="rag",
            estado="completado" if resultados_n2 else "escalado",
            detalle=_detalle_rag(resultados_n2, config.N2_MIN_SCORE),
            fuentes=fuentes_resumidas(resultados_n2),
        )
    )

    respuesta_n2 = _soporte_n2(pregunta, resultados_n2, confianza_n2)
    pasos.append(
        PasoRecorrido(
            id="soporte_n2",
            nombre="Soporte N2",
            tipo="agente",
            estado="escalado" if _pide_escalar_humano(respuesta_n2) else "final",
            detalle=(
                "N2 consulta el manual de configuración. "
                + (
                    "No localiza una respuesta suficientemente fiable."
                    if _pide_escalar_humano(respuesta_n2)
                    else "Responde con pasos técnicos."
                )
            ),
            fuentes=fuentes_resumidas(resultados_n2),
        )
    )

    if not _pide_escalar_humano(respuesta_n2):
        pasos.append(
            PasoRecorrido(
                id="clasificador_n2",
                nombre="Clasificador N2",
                tipo="clasificador",
                estado="final",
                detalle="El manual responde la consulta. El flujo termina.",
            )
        )
        return RespuestaSoporte(
            respuesta=respuesta_n2.strip(),
            nivel="N2",
            destino="fin",
            escalado=True,
            motivo="N1 no tenía cobertura suficiente",
            pasos=pasos,
            fuentes=fuentes_resumidas(resultados_n2),
            confianza_n1=confianza_n1,
            confianza_n2=confianza_n2,
        )

    pasos.append(
        PasoRecorrido(
            id="clasificador_n2",
            nombre="Clasificador N2",
            tipo="clasificador",
            estado="escalado",
            detalle="N2 no puede resolver con el manual. Se escala a humano.",
        )
    )
    pasos.append(
        PasoRecorrido(
            id="humano",
            nombre="Asistente Humano",
            tipo="humano",
            estado="final",
            detalle=f"Teléfono {config.HUMAN_PHONE} · {config.HUMAN_EMAIL}",
        )
    )
    return RespuestaSoporte(
        respuesta=_respuesta_humano(pregunta),
        nivel="Humano",
        destino="humano",
        escalado=True,
        motivo="Ni FAQ ni manual ofrecen una respuesta segura",
        pasos=pasos,
        fuentes=fuentes_resumidas(resultados_n2),
        confianza_n1=confianza_n1,
        confianza_n2=confianza_n2,
    )


def _rag_n1(pregunta: str) -> list[ResultadoBusqueda]:
    corpus = cargar_corpus()
    return corpus.retriever_faq.buscar(pregunta, config.TOP_K_N1)


def _rag_n2(pregunta: str) -> list[ResultadoBusqueda]:
    corpus = cargar_corpus()
    return corpus.retriever_manual.buscar(pregunta, config.TOP_K_N2)


def _soporte_n1(
    pregunta: str, resultados: list[ResultadoBusqueda], confianza: float
) -> str:
    if not _contexto_suficiente(resultados, confianza, config.N1_MIN_SCORE):
        return MARCA_ESCALAR_N2

    contexto = contexto_para_prompt(resultados)
    return generar_respuesta(
        [
            {
                "role": "system",
                "content": (
                    "Eres Soporte N1 del Router Smart WiFi 6 de Movistar. "
                    "Respondes solo preguntas frecuentes usando el contexto dado. "
                    f"Si el contexto no responde con claridad, escribe exactamente {MARCA_ESCALAR_N2}. "
                    "No uses conocimiento externo. Responde siempre en español de España."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Contexto FAQ:\n{contexto}\n\n"
                    f"Pregunta del cliente: {pregunta}\n\n"
                    "Respuesta de N1:"
                ),
            },
        ]
    )


def _soporte_n2(
    pregunta: str, resultados: list[ResultadoBusqueda], confianza: float
) -> str:
    if not _contexto_suficiente(resultados, confianza, config.N2_MIN_SCORE):
        return MARCA_ESCALAR_HUMANO

    contexto = contexto_para_prompt(resultados)
    return generar_respuesta(
        [
            {
                "role": "system",
                "content": (
                    "Eres Soporte N2, especialista técnico del Router Smart WiFi 6. "
                    "Usas únicamente el manual de configuración proporcionado. "
                    f"Si el manual no contiene una respuesta suficiente, escribe exactamente {MARCA_ESCALAR_HUMANO}. "
                    "Cuando respondas, da pasos claros, advierte si una acción puede cortar la conexión "
                    "y evita inventar menús no presentes en el manual."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Contexto del manual:\n{contexto}\n\n"
                    f"Pregunta del cliente: {pregunta}\n\n"
                    "Respuesta de N2:"
                ),
            },
        ]
    )


def _pide_escalar_n2(respuesta: str) -> bool:
    return respuesta.strip().upper().startswith(MARCA_ESCALAR_N2)


def _pide_escalar_humano(respuesta: str) -> bool:
    normalizada = respuesta.strip().upper()
    return normalizada.startswith(MARCA_ESCALAR_HUMANO) or normalizada.startswith(
        MARCA_ESCALAR_N2
    )


def _contexto_suficiente(
    resultados: list[ResultadoBusqueda], confianza: float, umbral: float
) -> bool:
    if confianza < umbral:
        return False
    coincidencias_utiles = {
        token
        for resultado in resultados[:3]
        for token in resultado.coincidencias
        if token not in TERMINOS_GENERICOS
    }
    return bool(coincidencias_utiles)


def _detalle_rag(resultados: list[ResultadoBusqueda], umbral: float) -> str:
    if not resultados:
        return "No se han recuperado fragmentos relevantes."
    mejor = resultados[0]
    return (
        f"Top {len(resultados)} fragmentos recuperados. "
        f"Mejor puntuación: {mejor.score:.2f}. Umbral: {umbral:.2f}."
    )


def _respuesta_humano(pregunta: str) -> str:
    return (
        "No encuentro una respuesta suficientemente segura en las preguntas frecuentes "
        "ni en el manual de configuración. Escalo la consulta a un asistente humano.\n\n"
        f"Resumen para soporte: {pregunta}\n\n"
        f"Teléfono: {config.HUMAN_PHONE}\n"
        f"Correo: {config.HUMAN_EMAIL}"
    )


def _respuesta_vacia() -> RespuestaSoporte:
    return RespuestaSoporte(
        respuesta="Escríbeme una pregunta sobre el Router Smart WiFi 6 y la reviso.",
        nivel="Entrada",
        destino="fin",
        escalado=False,
        motivo="Consulta vacía",
        pasos=[
            PasoRecorrido(
                id="entrada_llm",
                nombre="Entrada LLM",
                tipo="entrada",
                estado="pendiente",
                detalle="Esperando una pregunta del cliente.",
            )
        ],
        fuentes=[],
    )
