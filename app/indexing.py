"""Indexación del documento de FAQ en ChromaDB (alimenta el RAG del nivel 1).

Reutiliza el patrón de dia-4/chroma_persistente.py y dia-5/langgraph_example.py:
embeddings con nomic-embed-text, store persistente en disco e IDs deterministas
para poder reindexar sin duplicar vectores.

Troceamos por encabezados markdown (`##`) para que cada pregunta-respuesta de la
FAQ quede en su propio fragmento; así la recuperación devuelve respuestas
completas y no trozos cortados a mitad.
"""

import logging

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

from . import config

logger = logging.getLogger("proyecto_base.indexing")

embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)


def _get_store() -> Chroma:
    """Conecta (o crea) el store persistente del proyecto."""
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.PERSIST_DIR,
    )


def indexar() -> int:
    """Lee la FAQ, la trocea por preguntas y la indexa en Chroma.

    Es idempotente: usa IDs deterministas (`faq_{i}`), así que reiniciar el
    servidor reindexa sobre los mismos IDs sin crear duplicados. Devuelve el
    número de fragmentos indexados.
    """
    texto = config.FAQ_PATH.read_text(encoding="utf-8")

    # Cada `##` (una pregunta) se convierte en un fragmento independiente.
    # strip_headers=False mantiene el texto de la pregunta dentro del contenido,
    # no solo en los metadatos: así el embedding captura la pregunta y la
    # recuperación acierta cuando el usuario pregunta literalmente por ella.
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "pregunta")],
        strip_headers=False,
    )
    chunks = splitter.split_text(texto)

    # Enriquecer metadatos: fuente para citar y la pregunta como título.
    for c in chunks:
        c.metadata["source"] = config.FAQ_PATH.name

    store = _get_store()
    ids = [f"faq_{i}" for i in range(len(chunks))]
    store.add_documents(chunks, ids=ids)

    logger.info("Indexados %d fragmentos de la FAQ en '%s'", len(chunks), config.COLLECTION_NAME)
    return len(chunks)


def get_retriever():
    """Devuelve el retriever del nivel 1, reutilizado por el grafo."""
    store = _get_store()
    return store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.TOP_K},
    )
