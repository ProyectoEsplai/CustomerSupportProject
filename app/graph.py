"""Grafo de soporte con recepción y escalado en niveles (LangGraph).

El flujo:

    START ─► enrutar_por_nivel
                 │  nivel == 2 ──────────────────────────► nivel2 ─► END
                 │  nivel <= 1
                 ▼
             clasificar (¿la consulta es sobre Router Smart Wifi 6?)
                 │  GENERAL ──────────────────────────────► recepcion ─► END
                 │  ROUTER
                 ▼
             recuperar (RAG sobre la FAQ) ─► responder_nivel1
                                                  │
                                       decidir_escalado
                                       │  "ESCALAR" ──► nivel2 ─► END
                                       │  respuesta OK ──────────► END

- Recepción (nivel 0): atiende el inicio de la conversación —saludos, charla,
  agradecimientos, despedidas— sin tocar el RAG. Solo cuando el usuario plantea
  una duda sobre el modelo de router la consulta baja al nivel 1.
- Nivel 1: responde con preguntas frecuentes (RAG). Si la pregunta excede la FAQ,
  el propio agente emite el marcador `ESCALAR` y la consulta sube al nivel 2.
- Nivel 2: experto en Router Smart Wifi 6 avanzado (errores de instalación, soporte en conexiones, etc). 

El estado de la sesión (qué nivel está activo) vive fuera del grafo, en
sessions.py. El grafo solo decide el tema y el escalado de ESTA consulta concreta.
"""

import logging
from typing import List, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph

from . import config
from .indexing import get_retriever

logger = logging.getLogger("proyecto_base.graph")

# Marcador exacto que emite el nivel 1 cuando no puede resolver la consulta.
MARCA_ESCALADO = "ESCALAR"

llm = ChatOllama(model=config.LLM_MODEL, temperature=config.TEMPERATURE)


class EstadoSoporte(TypedDict):
    pregunta: str
    nivel: int  # nivel con el que entra la consulta (1 o 2)
    es_router: bool  # True si el clasificador detecta una consulta sobre el Router
    contexto: List[str]
    respuesta: str
    escalado: bool  # True si esta consulta acabó atendida por el nivel 2
    motivo: str  # "auto" | "feedback" | ""


# --- Prompts -----------------------------------------------------------------

# Recepción: clasifica si el mensaje es una consulta sobre Router o charla general.
# Devuelve una sola etiqueta para que el enrutado sea barato y predecible (igual
# que el clasificador de dia-5).
prompt_clasificador = ChatPromptTemplate.from_template(
    """Clasifica el mensaje del usuario en UNA de estas categorías:

- ROUTER: el usuario plantea una pregunta o duda sobre este modelo de router 
(problemas para instalar o configurar el router, dudas sobre el modelo de router, etc).
- GENERAL: saludos, presentaciones, charla, agradecimientos, despedidas o
  cualquier cosa que NO sea una consulta técnica sobre el router.

Responde EXACTAMENTE con una sola palabra: ROUTER o GENERAL. Nada más.

Mensaje: {pregunta}

Categoría:"""
)

# Recepción (nivel 0): da la bienvenida y conduce hacia una pregunta de Router Smart Wifi 6.
# No responde dudas técnicas; ese trabajo es del nivel 1.
prompt_recepcion = ChatPromptTemplate.from_template(
    """Eres el agente de recepción de un servicio de soporte del Router Smart Wifi 6.
Tu trabajo es atender el inicio de la conversación: saluda con amabilidad,
responde a la charla cordial (presentaciones, agradecimientos, despedidas) e
invita al usuario a contarte su duda sobre el Router Smart Wifi 6.

No respondas preguntas técnicas: si el usuario todavía no ha preguntado nada
sobre el Router Smart Wifi 6, anímale a hacerlo. Sé breve, cercano y natural.

Mensaje del usuario: {pregunta}

Respuesta:"""
)

# Nivel 1: RAG sobre la FAQ. Mantiene el patrón de los días previos (responder
# solo con el contexto, citar la fuente) y añade la regla de escalado.
prompt_nivel1 = ChatPromptTemplate.from_template(
    """Eres un agente de soporte de nivel 1. Respondes preguntas frecuentes
sobre el Router Smart Wifi 6 usando ÚNICAMENTE el siguiente contexto.

Reglas (síguelas en orden):
1. Si el contexto contiene la información para responder la pregunta, respóndela
   de forma clara y cita la fuente entre corchetes, por ejemplo [{fuente}].
2. Si el contexto NO contiene la información necesaria para responder, responde
   EXACTAMENTE con la palabra {marca} (en mayúsculas) y nada más. No intentes
   responder de memoria ni te disculpes: solo la palabra {marca}.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""
)

# Nivel 2: experto en el Router Smart Wifi 6.

# como {documentoN2}: habrá que definir esto en algún momento

prompt_nivel2 = ChatPromptTemplate.from_template(
    """Eres un agente de soporte de nivel 2, experto en el Router Smart Wifi 6.
Responde la siguiente pregunta de forma rigurosa y listando paso a paso las instrucciones. 
Si la pregunta es ambigua, explica las distintas interpretaciones. Toma como referencia los contenidos del {documentoN2}:
Qué es el Wi-Fi 6
¿Qué ventajas hay en tener este modelo?
Acceso al firmware de configuración vía web
Configurar el IDONT del GPON de fibra
Optimización y configuración de la red Wi-Fi
Configuración WiFi del menú básico
Configurar la red WiFi de invitados
Configuración WiFi del menú avanzado 
Banda de 2.4GHz  
Banda de 5GHz 
Deshabilitar el Band-steering y separar las bandas WiFi
Poner IP privada fija a cualquier dispositivo
Abrir puertos en el router
Configurar el modo monopuesto
Estado de la red con IPv6
Cambiar contraseña del router
Configurar el DNS dinámico o DynDNS
Opciones de administración generales
Configurar cuándo funciona el Wi-Fi

Pregunta: {pregunta}

Respuesta:"""
)


# --- Nodos -------------------------------------------------------------------


def enrutar_por_nivel(state: EstadoSoporte) -> str:
    """Router inicial: si la sesión ya está en nivel 2, salta directo al experto.

    En caso contrario pasa por recepción (clasificación) antes de decidir si la
    consulta merece el RAG del nivel 1.
    """
    return "nivel2" if state.get("nivel", 1) == 2 else "clasificar"


def clasificar_node(state: EstadoSoporte) -> dict:
    """RECEPCIÓN: decide si el mensaje es una consulta sobre el Router."""
    chain = prompt_clasificador | llm
    etiqueta = chain.invoke({"pregunta": state["pregunta"]}).content.strip().upper()
    es_router = "ROUTER" in etiqueta
    logger.info("Clasificación del mensaje: %r (es_router=%s)", etiqueta, es_router)
    return {"es_router": es_router}


def decidir_tema(state: EstadoSoporte) -> str:
    """Tras clasificar: consulta de el Router → nivel 1; charla → recepción."""
    return "recuperar" if state.get("es_router") else "recepcion"


def recepcion_node(state: EstadoSoporte) -> dict:
    """Nivel 0: atiende saludos y charla, e invita a preguntar sobre el Router."""
    chain = prompt_recepcion | llm
    respuesta = chain.invoke({"pregunta": state["pregunta"]}).content
    return {"respuesta": respuesta, "nivel": 0}


def recuperar_node(state: EstadoSoporte) -> dict:
    """NODO RAG: recupera fragmentos relevantes de la FAQ desde ChromaDB."""
    retriever = get_retriever()
    docs = retriever.invoke(state["pregunta"])
    contexto = [doc.page_content for doc in docs]
    logger.info("Recuperados %d fragmentos de la FAQ", len(contexto))
    return {"contexto": contexto}


def responder_nivel1_node(state: EstadoSoporte) -> dict:
    """Nivel 1: responde con la FAQ o emite el marcador de escalado."""
    contexto_texto = "\n\n".join(state["contexto"]) or "(sin contexto)"
    chain = prompt_nivel1 | llm
    respuesta = chain.invoke(
        {
            "contexto": contexto_texto,
            "pregunta": state["pregunta"],
            "fuente": config.FAQ_PATH.name,
            "marca": MARCA_ESCALADO,
        }
    ).content
    return {"respuesta": respuesta, "nivel": 1}


def decidir_escalado(state: EstadoSoporte) -> str:
    """Decide si el nivel 1 resolvió o hay que escalar al nivel 2."""
    if state["respuesta"].strip().upper() == MARCA_ESCALADO:
        logger.info("Nivel 1 no pudo resolver; escalando a nivel 2 (auto)")
        return "nivel2"
    return END


def nivel2_node(state: EstadoSoporte) -> dict:
    """Nivel 2: experto en el Router."""
    chain = prompt_nivel2 | llm
    respuesta = chain.invoke({"pregunta": state["pregunta"]}).content
    # Si llegamos por escalado automático conservamos el motivo; si la sesión ya
    # venía en nivel 2 (por feedback del usuario) lo reflejamos.
    motivo = state.get("motivo") or (
        "auto" if state.get("nivel", 1) == 1 else "feedback"
    )
    return {"respuesta": respuesta, "nivel": 2, "escalado": True, "motivo": motivo}


# --- Construcción del grafo --------------------------------------------------


def construir_grafo():
    builder = StateGraph(EstadoSoporte)
    builder.add_node("clasificar", clasificar_node)
    builder.add_node("recepcion", recepcion_node)
    builder.add_node("recuperar", recuperar_node)
    builder.add_node("responder_nivel1", responder_nivel1_node)
    builder.add_node("nivel2", nivel2_node)

    builder.add_conditional_edges(
        START,
        enrutar_por_nivel,
        {"clasificar": "clasificar", "nivel2": "nivel2"},
    )
    builder.add_conditional_edges(
        "clasificar",
        decidir_tema,
        {"recuperar": "recuperar", "recepcion": "recepcion"},
    )
    builder.add_edge("recepcion", END)
    builder.add_edge("recuperar", "responder_nivel1")
    builder.add_conditional_edges(
        "responder_nivel1",
        decidir_escalado,
        {"nivel2": "nivel2", END: END},
    )
    builder.add_edge("nivel2", END)

    return builder.compile()
