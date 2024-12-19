# Usa una imagen base ligera con Python
FROM python:3.9-slim

# Instala las dependencias necesarias para Chrome y ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    chromium-driver \
    chromium \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Configuración de entorno para ChromeDriver
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV GOOGLE_CHROME_BIN=/usr/bin/chromium

# Expone el puerto de la aplicación
EXPOSE 5000

# Define el comando para ejecutar la aplicación
CMD ["python", "app.py"]
