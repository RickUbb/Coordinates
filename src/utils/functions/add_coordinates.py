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
# Importa la función para obtener los códigos ISO
from src.services.iso_service import get_iso_from_country


# Configuración básica del logger para capturar errores
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def add_one_coordinate(db, collection_name, country: str, province: str, city: str,
                       lat_prov, lon_prov, lat_city, lon_city):
    """
    Agrega un documento de coordenadas a la colección de MongoDB si no existe ya.

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
        # Verificar la conexión a la base de datos
        db.command("ping")  # Si falla, lanzará una excepción ConnectionFailure
    except ConnectionFailure:
        logging.error(
            "No se pudo conectar a la base de datos. Verifica la conexión.")
        return

    # Preparar el documento a insertar
    data = {}
    if country != "NA":
        data['sub_1'] = country
        # Llamar a la función para obtener los códigos ISO del país
        iso_codes = get_iso_from_country(country)
        if 'error' in iso_codes:
            data['sub_1_alpha_2'] = 'NA'
            data['sub_1_alpha_3'] = 'NA'
            logging.error(f"Error al obtener los códigos ISO: {
                          iso_codes['error']}")

        else:
            # Asignar los códigos ISO al diccionario 'data'
            data['sub_1_alpha_2'] = iso_codes['cca2']
            data['sub_1_alpha_3'] = iso_codes['cca3']
    if province != "NA" and lat_prov is not None and lon_prov is not None:
        data['sub_3'] = normalize(province)
        data['lat_sub_3'] = lat_prov
        data['lon_sub_3'] = lon_prov
    if city != "NA" and lat_city is not None and lon_city is not None:
        data['sub_4'] = normalize(city)
        data['lat_sub_4'] = lat_city
        data['lon_sub_4'] = lon_city

    try:
        # Buscar si ya existe un documento con las mismas coordenadas
        existing_document = db[collection_name].find_one(data)

        # Si no se encuentra un documento, insertar uno nuevo
        if not existing_document and data:
            try:
                # Inserta el nuevo documento en la colección
                db[collection_name].insert_one(data)
                print("Documento insertado correctamente.")
            except DuplicateKeyError:
                logging.error(
                    "Error: El documento ya existe (clave duplicada).")
            except OperationFailure as e:
                logging.error(f"Fallo de operación en la inserción: {e}")
            except Exception as e:
                logging.error(f"Error inesperado durante la inserción: {e}")
        else:
            print("El documento ya existe en la base de datos.")

    except OperationFailure as e:
        logging.error(f"Error al ejecutar la consulta: {e}")
    except Exception as e:
        logging.error(f"Error inesperado durante la búsqueda: {e}")
