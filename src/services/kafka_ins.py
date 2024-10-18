"""
Este módulo se encarga de procesar mensajes de Kafka relacionados con documentos en MongoDB.

El módulo proporciona la función `process_kafka_message`, que maneja el flujo de procesamiento de un 
mensaje recibido de Kafka, incluyendo la recuperación del documento desde la base de datos, el 
procesamiento de los campos de región, la llamada a una API externa para obtener coordenadas, y la 
actualización del documento en la base de datos con las nuevas coordenadas.

Funciones principales:
- `process_kafka_message(document_id, collection_value)`: Procesa un mensaje de Kafka dado el ID 
  del documento y el tipo de documento, gestionando la obtención y actualización de datos en MongoDB, 
  así como la interacción con la API de coordenadas.
"""

import logging
from src.utils.functions.kafka_coordinates import (
    fetch_document_by_id,
    call_coordinates_api,
    update_data_in_document,
    db,
)

# Configuración del logger para capturar desde nivel WARNING
logging.basicConfig(
    level=logging.WARNING,  # Captura WARNING y superiores (ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Asegura que los mensajes se impriman en la consola (stdout)
    ]
)


def process_kafka_message_insi(document_id, collection_value):
    """
    Procesa un mensaje de Kafka que contiene el ID del documento y el tipo de documento.

    Este proceso incluye la recuperación del documento correspondiente de la base de datos MongoDB, 
    el procesamiento de los campos de región, la llamada a una API de coordenadas y la actualización 
    del documento con las nuevas coordenadas obtenidas.

    Args:
        document_id (str): ID del documento en MongoDB que se desea procesar.
        collection_value (str): Tipo de documento que determina la colección en MongoDB.

    Raises:
        Exception: Si ocurre un error en el procesamiento del mensaje o en cualquier parte del flujo.
    """
    try:
        # Recupera el documento a partir del ID y el tipo de colección
        document = fetch_document_by_id(collection_value, document_id)

        if not document:
            raise ValueError(f"Documento con _id={document_id} no encontrado.")

        # Procesa cada objeto de región en el documento
        for region_obj in document.get('pageFansCity', []):
            city = region_obj.get('city')
            country = region_obj.get('country')

            if not city:
                logging.warning(
                    f"[Documento ID: {document_id}] No se encontró el campo 'city' en el objeto: {region_obj}")
                continue

            try:
                # Procesa el campo de la región para obtener datos útiles
                region_data = {'city': city, 'contry': country}

                if not region_data:
                    logging.warning(
                        f"[Documento ID: {document_id}] No se pudo procesar los datos de city: {city}")
                    continue

                # Llama a la API de coordenadas con los datos de la región
                api_response = call_coordinates_api(region_data)

                if not api_response:
                    logging.warning(
                        f"[Documento ID: {document_id}] No se recibió respuesta de la API para la city: {city}")
                    continue

                # Extrae las nuevas coordenadas de la respuesta de la API
                new_lat = api_response.get('lat_subnivel_4')
                new_lon = api_response.get('lon_subnivel_4')

                if new_lat is None or new_lon is None:
                    logging.warning(
                        f"[Documento ID: {document_id}] Coordenadas no válidas para la city: {city}. lat={new_lat}, lon={new_lon}")
                    continue

                # Obtiene el nombre de la provincia o ciudad
                province = region_data.get(
                    'province', '') or region_data.get('city', '')

                if not province:
                    logging.warning(
                        f"[Documento ID: {document_id}] No se encontró el campo 'province' o 'city' en los datos de la región: {region_data}")
                    continue

                # Actualiza los datos de la región en el documento
                updated_document = update_data_in_document(
                    document, city, country, new_lat, new_lon)

                if not updated_document:
                    logging.warning(
                        f"[Documento ID: {document_id}] No se pudo actualizar el documento para la city: {city}")
                    continue

                # Actualiza el documento en MongoDB
                try:
                    db[collection_value].update_one(
                        {"_id": document_id}, {"$set": updated_document})
                    logging.info(
                        f"[Documento ID: {document_id}] Actualización exitosa para la city {city}: lat={new_lat}, lon={new_lon}")
                except Exception as e:
                    logging.error(
                        f"[Documento ID: {document_id}] Error al actualizar el documento en la base de datos para la city {city}: {str(e)}")

            except Exception as e:
                logging.exception(
                    f"[Documento ID: {document_id}] Error durante el procesamiento de la city {city}: {e}")

    except Exception as e:
        logging.exception(
            f"[Documento ID: {document_id}] Error durante el procesamiento del mensaje: {e}")
        raise
