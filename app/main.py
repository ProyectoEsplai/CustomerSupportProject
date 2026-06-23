"""Punto de entrada de consola para probar el grafo sin Streamlit."""

from __future__ import annotations

from .graph import procesar_consulta
from .indexing import resumen_indexacion


def main() -> None:
    resumen = resumen_indexacion()
    print("Soporte Router Smart WiFi 6")
    print(
        f"Fuentes cargadas: {resumen['fragmentos_faq_n1']} chunks N1, "
        f"{resumen['fragmentos_manual_n2']} chunks N2"
    )
    print("Escribe 'salir' para terminar.\n")

    while True:
        pregunta = input("Cliente> ").strip()
        if pregunta.lower() in {"salir", "exit", "quit"}:
            break
        respuesta = procesar_consulta(pregunta)
        print(f"\n[{respuesta.nivel}] {respuesta.respuesta}\n")


if __name__ == "__main__":
    main()
