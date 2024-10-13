"""
config.py

Este archivo contiene la configuración de la base de datos MongoDB y Kafka. Se utilizan variables de entorno 
para cargar las credenciales de la base de datos y Kafka usando `decouple.config`.
"""

# Importa config para leer las variables de entorno de un archivo .env
from decouple import config

# Configuración de MongoDB extraída de variables de entorno
mongo = {
    'mongodb_url': config('MONGODB_URL', default='mongodb://localhost:27017'),
    'mongodb_db_name': config('MONGODB_DB_NAME', default='mydatabase'),
    'mongodb_collection_name_coordinates': config('MONGODB_COLLECTION_NAME_COORDINATES', default='coordinates'),
    'mongodb_collection_name_error_coordinates': config('MONGODB_COLLECTION_NAME_ERROR_COORDINATES', default='coordinatesErrors')
}

# Configuración de Kafka extraída de variables de entorno
kafka = {
    # Cambiado a 'kafka:9092'
    'bootstrap_servers': config('KAFKA_BOOTSTRAP_SERVERS', default='kafka:9092'),
    'topic_name': config('KAFKA_TOPIC_NAME', default='my-topic'),
    'group_id': config('KAFKA_GROUP_ID', default='my-group'),
    'auto_offset_reset': config('KAFKA_AUTO_OFFSET_RESET', default='earliest'),
    'enable_auto_commit': config('KAFKA_ENABLE_AUTO_COMMIT', default=True, cast=bool)
}
