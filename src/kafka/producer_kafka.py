"""
producer_kafka.py

Este módulo define la lógica para un productor de Kafka que publica mensajes en un tópico.
El productor es utilizado para enviar datos a un broker Kafka.
"""

from confluent_kafka import Producer, KafkaError
import json
import logging
from config import kafka

# Inicializar el logger
logger = logging.getLogger(__name__)


class KafkaProducerService:
    """
    Clase que gestiona la publicación de mensajes en Kafka utilizando el productor.
    """

    def __init__(self):
        """Inicializa el productor de Kafka con la configuración proporcionada."""
        try:
            self.producer = Producer({
                'bootstrap.servers': kafka['bootstrap_servers'],
            })
            logger.info("Productor de Kafka inicializado correctamente.")
        except KafkaError as e:
            logger.error(f"Error al inicializar el productor de Kafka: {e}")
            raise

    def publish_message(self, topic, value):
        """
        Publica un mensaje en el tópico de Kafka especificado.

        Args:
            topic (str): El nombre del tópico donde se publicará el mensaje.
            value (dict): El mensaje a publicar en formato de diccionario.

        Returns:
            None
        """
        try:
            # Enviar el mensaje y asegurar que se publique en 10 segundos
            self.producer.produce(
                topic, value=json.dumps(value).encode('utf-8'))
            self.producer.flush(timeout=10)
            logger.info(f"Mensaje publicado correctamente en el tópico {
                        topic}: {value}")
        except KafkaError as e:
            logger.error(f"Error al publicar el mensaje en Kafka: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al publicar el mensaje: {e}")
            raise

    def close(self):
        """Cierra el productor de Kafka."""
        try:
            self.producer.flush()  # Asegura que se envíen todos los mensajes pendientes
            logger.info(
                "Todos los mensajes enviados, cerrando el productor de Kafka.")
        except KafkaError as e:
            logger.error(f"Error al cerrar el productor de Kafka: {e}")
            raise
        finally:
            logger.info("Productor de Kafka cerrado correctamente.")
