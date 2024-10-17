"""
Este módulo se encarga de procesar mensajes de Kafka para documentos almacenados en MongoDB. 
Extrae información de regiones, realiza consultas a una API externa para obtener coordenadas 
(latitud y longitud) basadas en dicha información, y luego actualiza los documentos en MongoDB 
con las coordenadas obtenidas.

Funciones principales del módulo:
- `get_collection_from_type(type_value)`: Determina la colección de MongoDB según el tipo de documento.
- `fetch_document_by_id(collection_name, document_id)`: Recupera un documento de MongoDB dado su ID.
- `process_region_field(region)`: Procesa el campo `region` de un documento y genera los datos correctos para la API.
- `call_coordinates_api(region_data)`: Realiza una solicitud a la API externa para obtener coordenadas.
- `update_region_data_in_document(document, region, new_lat, new_lon)`: Actualiza un documento con los nuevos datos de coordenadas.
- `process_kafka_message(document_id, type_value)`: Maneja el mensaje recibido por Kafka y ejecuta todo el proceso de actualización de coordenadas en MongoDB.

Este script utiliza los servicios de MongoDB para el almacenamiento de los documentos y una API externa 
para obtener las coordenadas de las regiones definidas en los documentos.
"""

from pymongo import MongoClient
from src.database.db_mongo import get_mongo_url, get_mongo_db_name
from config import kafka
import requests
import logging

# Configuración básica del logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializar MongoDB
try:
    MONGO_URI = get_mongo_url()
    client = MongoClient(MONGO_URI)
    db = client[get_mongo_db_name()]
except Exception as e:
    logging.critical(f"Error al conectar a MongoDB: {e}")
    raise SystemExit("No se pudo establecer la conexión a MongoDB.")

# Diccionario que mapea el "type" al nombre de la colección
COLLECTION_MAP = {
    "dp": "darkPostsFinal",
    "dpt": "darkPostTermsFinal",
    "insi": "IndiviInsiFb"
}

# Diccionario que mapea los valores del campo "region" a los parámetros de la API
REGION_MAP = {
    "State": "province",
    "Province": "province",
    "City": "city",
    "Country": "country"
}

# URL de la API externa
API_ENDPOINT = kafka['api_endpoint']


def get_collection_from_type(type_value):
    """
    Devuelve el nombre de la colección en MongoDB basado en el 'type' dado.

    Args:
        type_value (str): Valor del campo 'type' que define el tipo de documento.

    Returns:
        str: Nombre de la colección correspondiente.

    Raises:
        ValueError: Si el tipo es desconocido.
    """
    try:
        return COLLECTION_MAP[type_value]
    except KeyError:
        logging.error(f"Tipo desconocido: {type_value}")
        raise ValueError(f"Tipo desconocido: {type_value}")


def fetch_document_by_id(collection_name, document_id):
    """
    Busca un documento en la colección de MongoDB usando el _id.

    Args:
        collection_name (str): Nombre de la colección en MongoDB.
        document_id (str): ID del documento a buscar.

    Returns:
        dict: Documento encontrado o None si no se encuentra.

    Raises:
        Exception: Si ocurre un error al buscar el documento.
    """
    try:
        collection = db[collection_name]
        document = collection.find_one({"_id": document_id})
        if document is None:
            logging.warning(f"Documento con _id {
                            document_id} no encontrado en la colección {collection_name}.")
        return document
    except Exception as e:
        logging.error(f"Error al buscar el documento con _id {
                      document_id} en la colección {collection_name}: {e}")
        raise


def process_region_field(region):
    """
    Procesa el campo 'region' para extraer el tipo y el nombre de la región.

    Args:
        region (str): Campo de la región en el documento, en formato "Nombre | Tipo".

    Returns:
        dict: Diccionario con los datos de la región en el formato correcto para la API.

    Raises:
        Exception: Si ocurre un error al procesar el campo 'region'.
    """
    try:
        if " | " in region:
            # Separar la cadena en nombre de la región y tipo.
            parts = region.split(" | ")
            if len(parts) != 2:
                logging.warning(f"Formato inesperado para 'region': {region}")
                return {}

            region_name = parts[0].strip()  # Extraer el nombre de la región.
            # Extraer el tipo de la región (e.g., Province, City, etc.).
            region_type = parts[1].strip().title()

            if region_type in REGION_MAP:
                # Mapeamos el tipo de región a los parámetros que la API espera.
                return {REGION_MAP[region_type]: region_name}
            else:
                logging.warning(f"Tipo de región desconocido: {region_type}")
                return {}
        else:
            logging.warning(f"Formato inesperado para 'region': {region}")
            return {}

    except Exception as e:
        logging.error(f"Error al procesar el campo 'region': {e}")
        raise


def call_coordinates_api(region_data):
    """
    Llama a la API externa para obtener las coordenadas de la región.

    Args:
        region_data (dict): Datos de la región a enviar a la API.

    Returns:
        dict: Respuesta de la API con los datos de coordenadas.

    Raises:
        Exception: Si ocurre un error en la solicitud o en el procesamiento de la respuesta.
    """
    try:
        body = [region_data]
        logging.info(f"Enviando a la API: {body}")
        response = requests.post(API_ENDPOINT, json=body, headers={
                                 'Content-Type': 'application/json'})
        response.raise_for_status()

        results = response.json().get('results')
        if results and len(results) > 0:
            return results[0]
        else:
            logging.warning(
                "No se encontraron resultados en la respuesta de la API.")
            return None
    except requests.RequestException as e:
        logging.error(f"Error al llamar a la API: {e}")
        raise Exception(f"Error en API coordinates: {e}")
    except ValueError as ve:
        logging.error(f"Error al procesar la respuesta JSON: {ve}")
        raise


def update_region_data_in_document(document, region, new_lat, new_lon):
    """
    Actualiza los datos de latitud y longitud para la región especificada en el documento.

    Args:
        document (dict): Documento de MongoDB que contiene los datos de la región.
        region (str): Nombre de la región a actualizar.
        new_lat (float): Nueva latitud.
        new_lon (float): Nueva longitud.

    Returns:
        dict: Documento actualizado.

    Raises:
        ValueError: Si la región no se encuentra en el documento.
        Exception: Si ocurre un error al actualizar los datos.
    """
    try:
        updated = False

        for region_obj in document.get('region_distri', []):
            if region in region_obj['region']:
                region_obj['lat'] = new_lat
                region_obj['lon'] = new_lon
                region_obj['region'] = region
                updated = True

        if not updated:
            logging.error(f"No se encontró la región {
                          region} en el documento.")
            raise ValueError(f"Región {region} no encontrada.")

        return document
    except Exception as e:
        logging.error(
            f"Error al actualizar los datos de la región en el documento: {e}")
        raise
