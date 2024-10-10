"""
db_mongo.py

Este archivo maneja la conexión con MongoDB y proporciona funciones para acceder a la base de datos
y sus colecciones, como la colección de coordenadas. Utiliza la biblioteca `pymongo` para interactuar con MongoDB
y los detalles de configuración se encuentran en el archivo `config.py`.
"""

from config import mongo
import logging

# Configuración básica del logger para capturar errores
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_mongo_url() -> str:
    """
    Obtiene la URL de conexión a MongoDB desde la configuración.

    Returns:
        str: URL de conexión a MongoDB.

    Raises:
        KeyError: Si la clave 'mongodb_url' no está presente en la configuración.
    """
    try:
        return mongo['mongodb_url']
    except KeyError:
        logging.error(
            "La clave 'mongodb_url' no se encuentra en la configuración.")
        raise


def get_mongo_db_name() -> str:
    """
    Obtiene el nombre de la base de datos desde la configuración.

    Returns:
        str: Nombre de la base de datos.

    Raises:
        KeyError: Si la clave 'mongodb_db_name' no está presente en la configuración.
    """
    try:
        return mongo['mongodb_db_name']
    except KeyError:
        logging.error(
            "La clave 'mongodb_db_name' no se encuentra en la configuración.")
        raise


def get_coordinates_collection_name() -> str:
    """
    Obtiene el nombre de la colección de coordenadas desde la configuración.

    Returns:
        str: Nombre de la colección de coordenadas.

    Raises:
        KeyError: Si la clave 'mongodb_collection_name_coordinates' no está presente en la configuración.
    """
    try:
        name = mongo['mongodb_collection_name_coordinates']
        logging.info(f"Nombre de la colección de coordenadas: {
                     name}")  # Registro informativo
        return name
    except KeyError:
        logging.error(
            "La clave 'mongodb_collection_name_coordinates' no se encuentra en la configuración.")
        raise


def get_coordinates_error_collection_name() -> str:
    """
    Obtiene el nombre de la colección de coordenadas con errores desde la configuración.

    Returns:
        str: Nombre de la colección de coordenadas con errores.

    Raises:
        KeyError: Si la clave 'mongodb_collection_name_error_coordinates' no está presente en la configuración.
    """
    try:
        return mongo['mongodb_collection_name_error_coordinates']
    except KeyError:
        logging.error(
            "La clave 'mongodb_collection_name_error_coordinates' no se encuentra en la configuración.")
        raise
