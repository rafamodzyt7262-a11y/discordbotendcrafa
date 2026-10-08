FROM python:3.12-slim

# Instalar FFmpeg, dependencias de audio, libopus y utilidades
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libopus0 \
    libopus-dev \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Asegurar carpeta temporal de audio
RUN mkdir -p /app/temp_audio

# Exponer el puerto para el healthcheck de Railway
EXPOSE 8080

# Iniciar los 3 bots juntos 24/7 supervisados
CMD ["python", "run_all_3_bots.py"]
