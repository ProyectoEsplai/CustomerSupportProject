# Se recomienda una imagen oficial y ligera para Python
FROM python:3.11-slim

# Creamos y establecemos el directorio de trabajo dentro del contenedor
WORKDIR /workspace

# Actualizamos repositorios e instalamos dependencias del SO si son necesarias para compilar paquetes base
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos la lista de dependencias primero para aprovechar el caché de capas ("layer caching") de Docker
COPY requirements.txt .

# Instalamos las librerías
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos todo el proyecto
COPY . .

# Exponemos el puerto de Streamlit por defecto
EXPOSE 8501

# Levantamos la interfaz; garantizamos que '0.0.0.0' escuche para aceptar conexiones desde el host externo
CMD ["streamlit", "run", "streamlit_app.py", "--server.headless", "true", "--server.address", "0.0.0.0"]