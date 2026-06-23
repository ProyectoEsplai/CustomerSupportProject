"""Carga de PDFs y recuperación RAG ligera para N1 y N2.

La versión del curso usa Chroma y embeddings. Para este proyecto de aula usamos
un recuperador léxico local: no necesita GPU, no descarga modelos de embeddings
y mantiene separadas las fuentes de cada nivel.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from . import config


STOPWORDS = {
    "a",
    "al",
    "algo",
    "ante",
    "antes",
    "como",
    "con",
    "contra",
    "cual",
    "cuando",
    "de",
    "del",
    "desde",
    "donde",
    "dos",
    "el",
    "en",
    "entre",
    "es",
    "esa",
    "ese",
    "eso",
    "esta",
    "este",
    "esto",
    "ha",
    "hay",
    "la",
    "las",
    "le",
    "lo",
    "los",
    "mas",
    "me",
    "mi",
    "mis",
    "no",
    "o",
    "para",
    "pero",
    "por",
    "porque",
    "que",
    "se",
    "si",
    "sin",
    "sobre",
    "su",
    "sus",
    "te",
    "tu",
    "un",
    "una",
    "uno",
    "y",
    "ya",
}


@dataclass(frozen=True)
class Fragmento:
    id: str
    fuente: str
    texto: str
    pagina_inicio: int
    pagina_fin: int
    titulo: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoBusqueda:
    fragmento: Fragmento
    score: float
    coincidencias: tuple[str, ...]


class RecuperadorLexico:
    """BM25 pequeño y suficiente para corpus cortos de aula."""

    def __init__(self, fragmentos: list[Fragmento]) -> None:
        self.fragmentos = fragmentos
        self.frecuencias = [Counter(fragmento.tokens) for fragmento in fragmentos]
        self.longitudes = [len(fragmento.tokens) or 1 for fragmento in fragmentos]
        self.longitud_media = sum(self.longitudes) / max(len(self.longitudes), 1)
        self.idf = self._calcular_idf(fragmentos)

    def buscar(self, pregunta: str, top_k: int) -> list[ResultadoBusqueda]:
        tokens_pregunta = tokenizar(pregunta)
        if not tokens_pregunta:
            return []

        resultados: list[ResultadoBusqueda] = []
        for fragmento, frecuencias, longitud in zip(
            self.fragmentos, self.frecuencias, self.longitudes
        ):
            score = self._bm25(tokens_pregunta, frecuencias, longitud)
            if score <= 0:
                continue
            coincidencias = tuple(
                sorted({token for token in tokens_pregunta if token in frecuencias})
            )
            resultados.append(ResultadoBusqueda(fragmento, score, coincidencias))

        resultados.sort(key=lambda resultado: resultado.score, reverse=True)
        return resultados[:top_k]

    def _bm25(
        self, tokens_pregunta: list[str], frecuencias: Counter[str], longitud: int
    ) -> float:
        k1 = 1.4
        b = 0.72
        score = 0.0
        for token in set(tokens_pregunta):
            frecuencia = frecuencias.get(token, 0)
            if frecuencia == 0:
                continue
            denominador = frecuencia + k1 * (
                1 - b + b * longitud / max(self.longitud_media, 1)
            )
            score += self.idf.get(token, 0.0) * (frecuencia * (k1 + 1) / denominador)
        return score

    @staticmethod
    def _calcular_idf(fragmentos: list[Fragmento]) -> dict[str, float]:
        total = len(fragmentos)
        frecuencias_documento: Counter[str] = Counter()
        for fragmento in fragmentos:
            frecuencias_documento.update(set(fragmento.tokens))
        return {
            token: math.log((total - df + 0.5) / (df + 0.5) + 1)
            for token, df in frecuencias_documento.items()
        }


@dataclass(frozen=True)
class CorpusSoporte:
    faq: list[Fragmento]
    manual: list[Fragmento]
    retriever_faq: RecuperadorLexico
    retriever_manual: RecuperadorLexico


def tokenizar(texto: str) -> list[str]:
    limpio = unicodedata.normalize("NFKD", texto.lower())
    limpio = "".join(c for c in limpio if not unicodedata.combining(c))
    tokens = re.findall(r"[a-z0-9]{3,}", limpio)
    return [token for token in tokens if token not in STOPWORDS]


def contexto_para_prompt(resultados: list[ResultadoBusqueda]) -> str:
    bloques = []
    for posicion, resultado in enumerate(resultados, start=1):
        fragmento = resultado.fragmento
        paginas = _formatear_paginas(fragmento)
        bloques.append(
            "\n".join(
                [
                    f"[{posicion}] Fuente: {fragmento.fuente}, {paginas}",
                    f"Título: {fragmento.titulo}",
                    f"Coincidencias: {', '.join(resultado.coincidencias) or 'sin coincidencias'}",
                    fragmento.texto,
                ]
            )
        )
    return "\n\n---\n\n".join(bloques)


def fuentes_resumidas(resultados: list[ResultadoBusqueda]) -> list[str]:
    fuentes = []
    vistas = set()
    for resultado in resultados:
        fragmento = resultado.fragmento
        etiqueta = f"{fragmento.fuente}, {_formatear_paginas(fragmento)}"
        if etiqueta not in vistas:
            vistas.add(etiqueta)
            fuentes.append(etiqueta)
    return fuentes


@lru_cache(maxsize=1)
def cargar_corpus() -> CorpusSoporte:
    faq = _cargar_pdf_por_chunks(
        config.FAQ_PDF_PATH,
        fuente="FAQ Smart WiFi 6",
        prefijo="faq",
        max_chars=config.FAQ_CHUNK_CHARS,
    )
    manual = _cargar_pdf_por_chunks(
        config.MANUAL_PDF_PATH,
        fuente="Manual de configuración Smart WiFi 6",
        prefijo="manual",
        max_chars=config.MANUAL_CHUNK_CHARS,
    )
    return CorpusSoporte(
        faq=faq,
        manual=manual,
        retriever_faq=RecuperadorLexico(faq),
        retriever_manual=RecuperadorLexico(manual),
    )


def _cargar_pdf_por_chunks(
    path: Path, fuente: str, prefijo: str, max_chars: int
) -> list[Fragmento]:
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra la fuente RAG: {path}")

    paginas = _extraer_paginas(path)
    fragmentos: list[Fragmento] = []
    contador = 0
    for pagina, texto_pagina in paginas:
        for texto in _trocear_texto(texto_pagina, max_chars, config.CHUNK_OVERLAP):
            titulo = _inferir_titulo(texto, pagina, fuente)
            tokens = tuple(tokenizar(texto))
            if not tokens:
                continue
            contador += 1
            fragmentos.append(
                Fragmento(
                    id=f"{prefijo}_{contador}",
                    fuente=fuente,
                    texto=texto,
                    pagina_inicio=pagina,
                    pagina_fin=pagina,
                    titulo=titulo,
                    tokens=tokens,
                )
            )
    return fragmentos


def _extraer_paginas(path: Path) -> list[tuple[int, str]]:
    reader = PdfReader(str(path))
    paginas: list[tuple[int, str]] = []
    for indice, pagina in enumerate(reader.pages, start=1):
        texto = limpiar_texto(pagina.extract_text() or "")
        if texto:
            paginas.append((indice, texto))
    return paginas


def _trocear_texto(texto: str, max_chars: int, overlap: int) -> Iterable[str]:
    if len(texto) <= max_chars:
        yield texto
        return

    inicio = 0
    while inicio < len(texto):
        fin = min(inicio + max_chars, len(texto))
        corte = texto.rfind(". ", inicio, fin)
        if corte <= inicio + max_chars * 0.55:
            corte = texto.rfind("\n", inicio, fin)
        if corte <= inicio:
            corte = fin
        chunk = texto[inicio:corte].strip()
        if chunk:
            yield chunk
        if corte >= len(texto):
            break
        inicio = max(corte - overlap, 0)


def limpiar_texto(texto: str) -> str:
    texto = texto.replace("\x00", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    texto = re.sub(r"(?<!\n)\n(?!\n)", " ", texto)
    return texto.strip()


def _inferir_titulo(texto: str, pagina: int, fuente: str) -> str:
    lineas = [linea.strip(" .:-") for linea in texto.splitlines() if linea.strip()]
    if lineas:
        candidata = lineas[0]
        if len(candidata) > 90:
            candidata = candidata[:87].rstrip() + "..."
        return candidata
    return f"{fuente}, página {pagina}"


def _formatear_paginas(fragmento: Fragmento) -> str:
    if fragmento.pagina_inicio == fragmento.pagina_fin:
        return f"página {fragmento.pagina_inicio}"
    return f"páginas {fragmento.pagina_inicio}-{fragmento.pagina_fin}"
