"""
consumer_kafka.py

Este módulo define la lógica para un consumidor de Kafka.
El consumidor escucha un tópico y procesa los mensajes recibidos.
"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from config import kafka
from src.routes.CoordinatesRoutes import get_coordinates

# Inicializar el logger
logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """
    Clase que gestiona la recepción de mensajes desde Kafka utilizando el consumidor.
    """

    def __init__(self):
        """Inicializa el consumidor de Kafka con la configuración proporcionada."""
        try:
            self.consumer = KafkaConsumer(
                kafka['topic_name'],
                bootstrap_servers=kafka['bootstrap_servers'],
                group_id=kafka['group_id'],
                auto_offset_reset=kafka['auto_offset_reset'],
                enable_auto_commit=kafka['enable_auto_commit'],
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("Consumidor de Kafka inicializado correctamente.")
        except KafkaError as e:
            logger.error(f"Error al inicializar el consumidor de Kafka: {e}")
            raise

    def consume_messages(self):
        """
        Consume los mensajes desde el tópico de Kafka y los procesa con la API /coordinates.

        Returns:
            None
        """
        try:
            for message in self.consumer:
                logger.info(f"Mensaje recibido: {message.value}")
                try:
                    # Procesar el mensaje llamando a la función de tu API Flask
                    response = get_coordinates(message.value)
                    logger.info(
                        f"Respuesta de la API /coordinates: {response}")
                except Exception as e:
                    logger.error(f"Error al procesar el mensaje: {e}")
        except KafkaError as e:
            logger.error(f"Error al consumir mensajes desde Kafka: {e}")
            raise

    def close(self):
        """Cierra el consumidor de Kafka."""
        try:
            self.consumer.close()
            logger.info("Consumidor de Kafka cerrado correctamente.")
        except KafkaError as e:
            logger.error(f"Error al cerrar el consumidor de Kafka: {e}")
            raise
