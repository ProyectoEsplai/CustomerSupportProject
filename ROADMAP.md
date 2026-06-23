# Hoja de ruta - Soporte Router Smart WiFi 6

## Versión actual

- Interfaz Streamlit en español.
- Modelo local `gemma3:4b` servido por Ollama.
- RAG N1 sobre el PDF de 50 preguntas frecuentes.
- RAG N2 sobre el manual de configuración.
- Escalado final a asistente humano inventado.
- Recorrido visual de nodos por cada consulta.

## Mejoras posibles

1. Añadir evaluación automática con 15-20 preguntas de prueba.
2. Cambiar el recuperador léxico por embeddings si los equipos lo permiten.
3. Guardar sesiones en SQLite para revisar conversaciones de clase.
4. Añadir exportación de trazas a CSV para comparar rutas N1/N2/Humano.
5. Añadir selector de modelo para probar `gemma3:1b`, `gemma3:4b` y otros modelos locales.
