# Hoja de Ruta Rápida (1 Semana) - Soporte Técnico con Múltiples RAGs

La arquitectura ahora requiere instanciar tres recuperadores (retrievers) apuntando a tres colecciones distintas en ChromaDB. 

## 1. Estructura del Proyecto

```
proyecto_router/
├── data/
│   ├── faq/               # Documentos FAQ para N1
│   ├── manual_oficial/    # Manual del router para N2
│   ├── docs_avanzados/    # Documentación técnica para N3
│   └── chroma_db/         # Persistencia de las 3 colecciones
├── src/
│   ├── config.py          # Modelos, temperaturas, parámetros de chunking
│   ├── vector_stores.py   # Script para procesar PDFs y poblar las 3 colecciones
│   ├── prompts.py         # Prompts específicos para N1, N2, N3 y Clasificador
│   ├── agents.py          # Funciones de nodo y lógica de invocación a retrievers
│   ├── graph.py           # StateGraph y enrutamiento (escalado)
│   └── main.py            # Punto de entrada
└── tests/
    └── harness.py         # Casos de prueba automatizados
```

## 2. División de Responsabilidades (3 Integrantes)

### Integrante 1: Datos y Vector Stores
* **Objetivo:** Garantizar que cada nivel reciba el fragmento correcto.
* **Tareas:**
  * Configurar `vector_stores.py` para crear 3 `collection_name` separadas en la misma instancia de ChromaDB (ej. `soporte_n1_faq`, `soporte_n2_manual`, `soporte_n3_adv`).
  * Ajustar el `chunk_size` por nivel (FAQ: chunks pequeños; Manual: chunks medianos; Avanzado: chunks grandes con mayor *overlap*).
  * Exponer 3 objetos `retriever` para que los use el resto del equipo.

### Integrante 2: Arquitectura del Grafo (LangGraph)
* **Objetivo:** Controlar el flujo y las condiciones de escalado.
* **Tareas:**
  * Diseñar el `SupportState` incluyendo `current_level` y `escalation_reason`.
  * Programar las transiciones: Clasificador -> `node_n1`. Si N1 falla -> `node_n2`. Si N2 falla -> `node_n3`. Si N3 falla -> `mock_ticket`.
  * Escribir la lógica de evaluación en las aristas condicionales (ej. buscar palabras clave como "ESCALAR" en la salida del LLM para activar el salto al siguiente nodo).

### Integrante 3: Prompts e Invocación de Nodos
* **Objetivo:** Definir el comportamiento del LLM en cada etapa.
* **Tareas:**
  * Crear prompts para N1, N2 y N3. Cada prompt debe incluir una instrucción estricta de responder "ESCALAR" (o un token específico) si el contexto inyectado por su RAG no responde la consulta.
  * Implementar las funciones de nodo en `agents.py` que invocan al retriever correspondiente (N1 invoca `retriever_faq`, etc.) y luego pasan el contexto al LLM.
  * Diseñar el prompt del mock ticket (extrae el resumen del problema no resuelto y lo formatea).


## 3. Cronograma Diario (Días 1 a 7)

* **Día 1: Ingesta de Datos y Setup.**
  * I1: Carga los PDFs, configura y puebla ChromaDB con las 3 colecciones.
  * I2: Define el estado compartido (`TypedDict`) y crea el esqueleto del grafo en LangGraph.
  * I3: Redacta los prompts iniciales para los 3 niveles y el generador de tickets.
* **Día 2-3: Desarrollo de Nodos y RAG.**
  * I1: Prueba manual de los retrievers (ej. asegurar que el RAG N2 no devuelve cosas del N3).
  * I3: Integra los retrievers en las funciones de nodo (`node_n1`, `node_n2`, `node_n3`). Ajusta prompts según resultados.
* **Día 4-5: Integración del Grafo y Escalado.**
  * I2: Une los nodos de I3 en el `StateGraph`. Implementa la lógica de las aristas condicionales (escalado entre N1, N2, N3 y Ticket).
  * Todo el equipo: Primer end-to-end con consultas simples directamente en `main.py`.
* **Día 6: Refinamiento de Escalado.**
  * Ajustar por qué y cuándo un agente escala. Evitar que un agente alucine una respuesta en lugar de escalar. Modificar la temperatura del LLM si es necesario.
* **Día 7: Pruebas y Cierre.**
  * Ejecutar el `harness.py` con un banco de 20 preguntas (5 resolubles por N1, 5 por N2, 5 por N3 y 5 sin solución para forzar Ticket).
  * Corrección de errores finales y código limpio.