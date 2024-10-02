"""
add_coordinates.py

Este módulo contiene una función que permite agregar un conjunto de coordenadas (país, provincia y ciudad) a 
una colección de MongoDB. Verifica si ya existen las coordenadas antes de insertar un nuevo documento y maneja 
diversos errores de conexión y operación.
"""

import logging  # Para el registro de mensajes de error y eventos
# Excepciones específicas de pymongo
from pymongo.errors import ConnectionFailure, DuplicateKeyError, OperationFailure
# Importa la función de normalización de texto
from src.utils.functions.normalize_text import normalize

# Configuración básica del logger para capturar errores
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def add_one_coordinate(db, collection_name, country: str, province: str, city: str,
                       lat_prov, lon_prov, lat_city, lon_city):
    """
    Agrega un documento de coordenadas a la colección de MongoDB si no existe ya.

    La función primero normaliza los valores de entrada (país, provincia, ciudad) y luego verifica si ya 
    existe un documento con esas coordenadas. Si no existe, lo inserta en la colección especificada.

    Args:
        db (Database): La instancia de la base de datos MongoDB.
        collection_name (str): El nombre de la colección donde se insertarán las coordenadas.
        country (str): El nombre del país.
        province (str): El nombre de la provincia.
        city (str): El nombre de la ciudad.
        lat_prov (float): La latitud de la provincia.
        lon_prov (float): La longitud de la provincia.
        lat_city (float): La latitud de la ciudad.
        lon_city (float): La longitud de la ciudad.

    Returns:
        None
    """

    try:
        # Verificar la conexión a la base de datos con un comando simple de 'ping'
        db.command("ping")  # Si falla, lanzará una excepción ConnectionFailure
    except ConnectionFailure:
        # Registra un error
        logging.error(
            "No se pudo conectar a la base de datos. Verifica la conexión.")
        return  # Termina la función si no hay conexión

    try:
        # Buscar si ya existe un documento con las mismas coordenadas
        existing_document = db[collection_name].find_one({
            'sub_1': normalize(country),  # Normaliza el país
            'sub_3': normalize(province),  # Normaliza la provincia
            'lat_sub_3': lat_prov,  # Latitud de la provincia
            'lon_sub_3': lon_prov,  # Longitud de la provincia
            'sub_4': normalize(city),  # Normaliza la ciudad
            'lat_sub_4': lat_city,  # Latitud de la ciudad
            'lon_sub_4': lon_city   # Longitud de la ciudad
        })

        # Si no se encuentra un documento con estas coordenadas, insertar uno nuevo
        if not existing_document:
            data = {
                'sub_1': normalize(country),  # País normalizado
                'sub_3': normalize(province),  # Provincia normalizada
                'lat_sub_3': lat_prov,  # Latitud de la provincia
                'lon_sub_3': lon_prov,  # Longitud de la provincia
                'sub_4': normalize(city),  # Ciudad normalizada
                'lat_sub_4': lat_city,  # Latitud de la ciudad
                'lon_sub_4': lon_city   # Longitud de la ciudad
            }

            try:
                # Inserta el nuevo documento en la colección
                db[collection_name].insert_one(data)
                print("Documento insertado correctamente.")
            except DuplicateKeyError:
                # Error si la clave es duplicada
                logging.error(
                    "Error: El documento ya existe (clave duplicada).")
            except OperationFailure as e:
                # Error en la operación de inserción
                logging.error(f"Fallo de operación en la inserción: {e}")
            except Exception as e:
                logging.error(f"Error inesperado durante la inserción: {
                              e}")  # Cualquier otro error inesperado
        else:
            # Si el documento ya existe, no inserta nada
            print("El documento ya existe en la base de datos.")

    except OperationFailure as e:
        logging.error(f"Error al ejecutar la consulta: {
                      e}")  # Error durante la búsqueda
    except Exception as e:
        # Otros errores inesperados en la búsqueda
        logging.error(f"Error inesperado durante la búsqueda: {e}")
