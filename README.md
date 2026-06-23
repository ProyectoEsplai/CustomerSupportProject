# Soporte Router Smart WiFi 6 con agentes

Aplicación Streamlit para atención al cliente sobre el Router Smart WiFi 6 de
Movistar. El flujo sigue el esquema del curso: recuperación RAG, agentes por
nivel, clasificadores de escalado y trazabilidad visual del recorrido.

## Flujo implementado

1. **Entrada LLM** recibe la pregunta y la entrega a N1.
2. **RAG N1** recupera fragmentos del PDF de preguntas frecuentes:
   `Las 50 preguntas más frecuentes sobre el router Smart WiFi 6 de Movistar.pdf`.
3. **Soporte N1** responde solo si la FAQ contiene información suficiente.
4. **Clasificador N1** termina o escala a N2.
5. **RAG N2** recupera fragmentos del manual:
   `manual-de-configuracion-del-router-movistar_compress.pdf`.
6. **Soporte N2** responde con pasos técnicos usando solo el manual.
7. **Clasificador N2** termina o escala a **Asistente Humano**.

Contacto humano inventado para la demo:

- Teléfono: `900 123 456`
- Correo: `soporte.smartwifi6@example.com`

## Requisitos

- Python 3.10 o superior.
- Ollama abierto en `http://localhost:11434`.
- Modelo descargado:

```bash
ollama pull gemma3:4b
```

- Dependencias Python:

```bash
pip install -r requirements.txt
```

## Ejecución

Desde esta carpeta:

```bash
python -m streamlit run streamlit_app.py --server.headless true --browser.gatherUsageStats false
```

En Windows también puedes ejecutar:

```bash
run_streamlit.bat
```

La app carga los dos PDFs desde la carpeta superior del curso. Si cambias los
nombres de los PDFs, actualiza las rutas en `app/config.py`.

## Estructura

```text
CustomerSupportProject/
├── app/
│   ├── config.py          # rutas, modelo, umbrales y contacto humano
│   ├── documents.py       # extracción de PDFs y recuperador léxico BM25
│   ├── graph.py           # nodos, estado, clasificación y escalado
│   ├── indexing.py        # compatibilidad con la idea de indexación
│   ├── main.py            # prueba rápida por consola
│   ├── ollama_client.py   # cliente HTTP para Ollama sin dependencias extra
│   └── schemas.py         # tipos compartidos
├── requirements.txt
└── streamlit_app.py       # interfaz Streamlit
```

## Notas didácticas

- El RAG es ligero: usa búsqueda léxica local para no exigir otro modelo de
  embeddings en equipos modestos.
- Los prompts obligan a N1 y N2 a escalar si su contexto no responde.
- La pantalla muestra cada nodo ejecutado y las fuentes recuperadas en cada paso.

---
---

## Dockerización:

- Un contenedor creado a partir de un Dockerfile con python y las dependencias que necesita

- Otros dos contenedores creados desde el Docker compose:
   1. Ollama
   2. Ollama-init, cuyopropósito es esperar a que Ollama se levante y descargar automáticamente el modelo gemma3:4b antes de que Streamlit comience

### Comando para lanzarlo:

```sh
docker-compose up --build
```

### Flujo:

1. Docker iniciará el servidor de Ollama vacío.
2. Inmediatamente el script `ollama-init` interceptará el contenedor, comenzará a descargar el modelo, y retendrá el arranque de la app.
3. Al finalizar, la app Streamlit se construirá en su contenedor, iniciará, se conectará a Ollama de forma limpia y será alcanzable accediendo en el host a `http://localhost:8501`.
