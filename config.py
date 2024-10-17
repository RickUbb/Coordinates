"""
config.py

Este archivo contiene la configuración de la base de datos MongoDB. Se utilizan variables de entorno 
para cargar las credenciales de la base de datos usando `decouple.config`.
"""

# Importa config para leer las variables de entorno de un archivo .env
from decouple import config

# Configuración de MongoDB extraída de variables de entorno
mongo = {
    # URL de conexión a MongoDB
    'mongodb_url': config('MONGODB_URL', default='mongodb://localhost:27017'),
    # Nombre de la base de datos
    'mongodb_db_name': config('MONGODB_DB_NAME', default='mydatabase'),
    # Nombre de la colección
    'mongodb_collection_name_coordinates': config('MONGODB_COLLECTION_NAME_COORDINATES', default='coordinates'),
    # Nombre de la colección de errores
    'mongodb_collection_name_error_coordinates': config('MONGODB_COLLECTION_NAME_ERROR_COORDINATES', default='coordinatesErrors')
}

kafka = {
    'kafka_topic': config("KAFKA_TOPIC", default='to-enrich-lat-lon'),
    'kafka_bootstrap_servers': config("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
    'group_id': config("GROUP_ID", default='coordinates-group'),
    'kafka_auto_offset_reset': config("KAFKA_AUTO_OFFSET_RESET", default='earliest'),
    'kafka_enable_auto_commit': config("KAFKA_ENABLE_AUTO_COMMIT", default="True"),
    'api_endpoint': config("API_ENDPOINT", default="http://app:5000/coordinates/")
}
