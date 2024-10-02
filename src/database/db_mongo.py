"""
db_mongo.py

Este archivo maneja la conexión con MongoDB y proporciona funciones para acceder a la base de datos
y sus colecciones, como la colección de coordenadas. Utiliza la biblioteca `pymongo` para interactuar con MongoDB
y los detalles de configuración se encuentran en el archivo `config.py`.
"""

from pymongo import MongoClient  # Importa el cliente de MongoDB desde pymongo
from config import mongo  # Importa la configuración desde el archivo config.py


def get_database():
    """
    Establece una conexión con la base de datos MongoDB y retorna la instancia de la base de datos.

    Esta función utiliza el cliente de MongoDB (`MongoClient`) para conectarse a la base de datos usando la URL
    y el nombre de la base de datos definidos en el archivo de configuración.

    Returns:
        database (Database): La instancia de la base de datos configurada en el archivo de configuración.
    """
    client = MongoClient(
        # Crea un cliente MongoDB utilizando la URL de conexión desde la configuración.
        mongo['mongodb_url']
    )
    # Obtiene la base de datos especificada por 'mongodb_db_name' en la configuración.
    database = client[mongo['mongodb_db_name']]
    return database  # Retorna la instancia de la base de datos.


def get_coordinates_collection():
    """
    Obtiene la colección de coordenadas desde la base de datos MongoDB.

    Llama a la función `get_database` para establecer la conexión con la base de datos y luego accede a la colección
    de coordenadas que está configurada bajo el nombre `mongodb_collection_name_coordinates` en el archivo de configuración.

    Returns:
        collection (Collection): La colección de coordenadas dentro de la base de datos.
    """
    database = get_database(
        # Llama a la función get_database para obtener la instancia de la base de datos.
    )

    # Retorna la colección de coordenadas usando el nombre de la colección definido en la configuración.
    return database[mongo['mongodb_collection_name_coordinates']]
