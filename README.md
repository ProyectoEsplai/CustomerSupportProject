# proyecto_base — Chatbot de soporte Python con escalado

Aplicación FastAPI que integra las piezas del curriculum (RAG con Chroma,
enrutado con LangGraph, agentes con Ollama) en un chatbot de soporte sobre
Python con **recepción + escalado en niveles**.

- **Recepción (Nivel 0)** — atiende el inicio de la conversación: saludos, charla
  cordial, agradecimientos y despedidas. Un clasificador decide si el mensaje es
  una consulta sobre Python; solo entonces la consulta baja al Nivel 1. Así el
  RAG no se dispara con un simple "hola".
- **Nivel 1** — atiende preguntas frecuentes con RAG sobre `data/faq_python.md`
  (50 FAQ de Python básico/intermedio) indexado en ChromaDB. Si la pregunta
  excede la FAQ, **el propio agente decide escalar** (emite el marcador `ESCALAR`).
- **Nivel 2** — experto en Python avanzado (programación funcional, decorators,
  composición de funciones). Atiende lo que el nivel 1 no resuelve, o cuando el
  usuario marca una respuesta como insatisfactoria.
- Si el usuario queda a gusto, puede **finalizar la sesión**.

## Requisitos

- [Ollama](https://ollama.com) corriendo en `http://localhost:11434`.
- Modelos descargados (`ollama list` para comprobar):
  - `qwen3:8b` (nivel 1 y nivel 2)
  - `nomic-embed-text` (embeddings)
- Dependencias del repo ya instaladas (`uv sync`). No añade dependencias nuevas.

## Cómo ejecutar

Desde la raíz del repo (`pildora-ai/`):

```bash
uv run uvicorn proyecto_base.app.main:app --reload
```

Al arrancar, indexa la FAQ en `proyecto_base/chroma_db/` (idempotente: usa IDs
deterministas, reiniciar no duplica vectores). Luego abre:

- **UI de chat**: http://localhost:8000/
- **Swagger / API**: http://localhost:8000/docs

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/` | Interfaz de chat web |
| `POST` | `/chat` | Envía un mensaje. Body: `{"mensaje": "...", "session_id": "...", "feedback": "insatisfecho"}` |
| `POST` | `/session/{id}/finalizar` | Cierra la sesión (usuario a gusto) |
| `GET`  | `/session/{id}` | Estado e historial (depuración) |
| `GET`  | `/health` | Comprobación de vida |

`session_id` y `feedback` son opcionales. La primera llamada sin `session_id`
crea una sesión nueva y devuelve su id.

## Cómo se dispara el escalado

1. **Automático**: el nivel 1 responde con la FAQ; si la pregunta requiere
   conocimiento avanzado o no está cubierta, emite `ESCALAR` y la consulta pasa
   al nivel 2 (`motivo: "auto"`).
2. **Por feedback**: si el usuario envía `feedback: "insatisfecho"`, la sesión
   sube a nivel 2 y todas las consultas siguientes las atiende el experto
   (`motivo: "feedback"`).

## Estructura

```
proyecto_base/
├── data/faq_python.md     # 50 FAQ de Python (fuente del RAG nivel 1)
├── static/index.html      # UI de chat
├── chroma_db/             # store Chroma (se crea al arrancar; gitignored)
└── app/
    ├── config.py          # modelos, rutas absolutas, colección
    ├── indexing.py        # FAQ → chunks → Chroma + retriever
    ├── graph.py           # StateGraph: recepción → nivel1/nivel2 y escalado
    ├── sessions.py        # sesiones en memoria
    ├── schemas.py         # modelos Pydantic
    └── main.py            # app FastAPI (lifespan + endpoints)
```

## Límites (proyecto didáctico)

- Sesiones en memoria: se pierden al reiniciar el servidor.
- Sin autenticación (uso local).
