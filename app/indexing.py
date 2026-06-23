"""Compatibilidad con la idea de indexación del curso.

En lugar de Chroma persistente, este proyecto prepara en memoria los fragmentos
de FAQ y manual usando `documents.cargar_corpus()`.
"""

from __future__ import annotations

from .documents import CorpusSoporte, cargar_corpus


def indexar() -> CorpusSoporte:
    """Carga y tokeniza las fuentes RAG de N1 y N2."""
    return cargar_corpus()


def resumen_indexacion() -> dict[str, int]:
    corpus = cargar_corpus()
    return {
        "fragmentos_faq_n1": len(corpus.faq),
        "fragmentos_manual_n2": len(corpus.manual),
    }
