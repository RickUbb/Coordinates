"""
db_mongo.py

Este archivo maneja la conexión con MongoDB y proporciona funciones para acceder a la base de datos
y sus colecciones, como la colección de coordenadas. Utiliza la biblioteca `pymongo` para interactuar con MongoDB
y los detalles de configuración se encuentran en el archivo `config.py`.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from config import mongo
import logging

# Configuración básica del logger para capturar errores
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_database():
    """
    Establece una conexión con la base de datos MongoDB y retorna la instancia de la base de datos.

    Esta función utiliza el cliente de MongoDB (`MongoClient`) para conectarse a la base de datos usando la URL
    y el nombre de la base de datos definidos en el archivo de configuración.

    Returns:
        database (Database): La instancia de la base de datos configurada en el archivo de configuración.
    """
    try:
        client = MongoClient(mongo['mongodb_url'])
        database = client[mongo['mongodb_db_name']]
        return database
    except (ConnectionFailure, ConfigurationError) as e:
        logging.error(f"Error al conectar con la base de datos MongoDB: {e}")
        return None


def get_coordinates_collection():
    """
    Obtiene la colección de coordenadas desde la base de datos MongoDB.

    Llama a la función `get_database` para establecer la conexión con la base de datos y luego accede a la colección
    de coordenadas que está configurada bajo el nombre `mongodb_collection_name_coordinates` en el archivo de configuración.

    Returns:
        collection (Collection): La colección de coordenadas dentro de la base de datos.
    """
    database = get_database()
    if database:
        try:
            collection = database[mongo['mongodb_collection_name_coordinates']]
            return collection
        except KeyError as e:
            logging.error(f"Error al acceder a la colección: {e}")
            return None
    else:
        logging.error("No se pudo obtener la base de datos.")
        return None
