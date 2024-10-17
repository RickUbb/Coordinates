# Usar una imagen base de Python
FROM python:3.12.2-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requisitos en el contenedor
COPY requirements.txt requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del proyecto en el contenedor
COPY . .

# Expone el puerto en el que correrá la aplicación
EXPOSE 5000

# Establece las variables de entorno
ENV FLASK_APP=main.py
ENV FLASK_ENV=development

# Comando para correr la aplicación Flask y el consumidor de Kafka
CMD ["sh", "-c", "PYTHONPATH=/app python main.py & PYTHONPATH=/app python src/services/kafka_enrichment_consumer.py"]

# Comando para correr la aplicación Flask y el consumidor de Kafka
#CMD ["sh", "-c", "python main.py & python src/services/kafka_enrichment_consumer.py"]
