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
    'mongodb_collection_name_coordinates': config('MONGODB_COLLECTION_NAME_COORDINATES', default='coordinates')
}
