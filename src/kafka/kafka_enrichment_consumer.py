"""
Este módulo se encarga de consumir mensajes de un tópico de Kafka, procesar la información de 
coordenadas utilizando la función `process_kafka_message`, y manejar el registro de eventos a través de 
logging.

El módulo se suscribe a un tópico específico en Kafka y deserializa los mensajes recibidos en formato 
JSON. Los mensajes deben contener los campos 'id' y 'type' para su procesamiento adecuado. 

Funciones principales:
- `process_message(id_value, collection_value)`: Procesa un mensaje de Kafka dado su ID y tipo.
- `consume_messages()`: Escucha continuamente el tópico de Kafka para consumir mensajes y 
  manejar su procesamiento.
"""

import os  # Importa el módulo os para acceder a variables de entorno
import json  # Importa el módulo json para trabajar con datos en formato JSON
import logging  # Importa el módulo logging para registrar eventos
# Importa la clase Consumer de la biblioteca confluent_kafka
from confluent_kafka import Consumer
# Importa la función para procesar mensajes
from src.services.kafka_dp import process_kafka_message_dp
from src.services.kafka_ins import process_kafka_message_insi
# Importa la función para obtener la colección
from src.utils.functions.kafka_coordinates import get_collection_from_type
from config import kafka  # Importa la configuración de Kafka

# Configuración del logging
# Establece el nivel de logging a DEBUG
logging.basicConfig(level=logging.DEBUG)
# Crea un logger con el nombre del módulo actual
logger = logging.getLogger(__name__)

# Define el tópico de Kafka
KAFKA_TOPIC = kafka['kafka_topic']  # Asigna el tópico de Kafka a una variable

# Inicializa el consumidor de Kafka con la configuración especificada
consumer = Consumer({
    # Dirección de los servidores de Kafka
    'bootstrap.servers': kafka['kafka_bootstrap_servers'],
    'group.id': kafka['group_id'],  # Identificador del grupo de consumidores
    # Configuración para leer los mensajes desde el principio
    'auto.offset.reset': kafka['kafka_auto_offset_reset']
})

# Suscribe el consumidor al tópico definido
consumer.subscribe([KAFKA_TOPIC])


def process_message(id_value, collection_value, type_value):
    """
    Procesa un mensaje de Kafka dado su ID y el nombre de la colección correspondiente.

    Args:
        id_value (str): El ID del documento que se va a procesar.
        collection_value (str): El nombre de la colección que se va a procesar.

    Raises:
        Exception: Si ocurre un error durante el procesamiento del mensaje.
    """
    logger.debug(f"Procesando mensaje con id: {id_value} de la colección: {
                 collection_value}")  # Log de depuración
    try:
        if (type_value == "dp"):
            process_kafka_message_dp(id_value, collection_value)

        if (type_value == "dpt"):
            process_kafka_message_dp(id_value, collection_value)

        if (type_value == "insi"):
            process_kafka_message_insi(id_value, collection_value)

    except Exception as e:
        logger.error(f"Error al procesar el mensaje con id {id_value} y colección {
                     collection_value}: {e}")  # Log de error si hay una excepción


def consume_messages():
    """
    Escucha continuamente el tópico de Kafka para consumir mensajes y manejar su procesamiento.

    Raises:
        Exception: Si ocurre un error inesperado durante la deserialización o procesamiento del mensaje.
    """
    while True:  # Bucle infinito para consumir mensajes continuamente
        msg = consumer.poll(1.0)  # Espera un mensaje durante 1 segundo
        if msg is None:  # Si no hay mensajes
            continue  # Continúa con la siguiente iteración

        if msg.error():  # Si hay un error en el mensaje
            logger.error(f"Error en el mensaje: {msg.error()}")  # Log de error
            continue  # Continúa con la siguiente iteración

        try:
            # Decodifica el valor del mensaje a UTF-8
            message_value = msg.value().decode('utf-8')
            # Log de depuración
            logger.debug(f"Mensaje recibido: {message_value}")

            # Deserializa el mensaje JSON
            message_data = json.loads(message_value)
            logger.debug(f"Datos deserializados: {
                         message_data}")  # Log de depuración

            # Verifica que el mensaje contenga los campos necesarios
            if 'id' in message_data and 'type' in message_data:
                id_value = message_data['id']  # Extrae el ID del mensaje
                type_value = message_data['type']  # Extrae el tipo del mensaje
                collection_value = get_collection_from_type(
                    type_value)  # Obtiene la colección correspondiente
                # Procesa el mensaje
                process_message(id_value, collection_value, type_value)
            else:
                # Log de advertencia si faltan campos
                logger.warning(
                    "El mensaje no contiene los campos 'id' y 'type' necesarios.")
        except json.JSONDecodeError as e:  # Captura excepciones de deserialización JSON
            logger.error(f"Error al deserializar el mensaje JSON: {
                         e}")  # Log de error
        except Exception as e:  # Captura cualquier otra excepción
            logger.error(f"Ocurrió un error inesperado: {e}")  # Log de error


if __name__ == "__main__":  # Verifica si el script se está ejecutando directamente
    logger.info("Iniciando consumidor Kafka...")  # Log de información
    consume_messages()  # Inicia la función de consumo de mensajes
