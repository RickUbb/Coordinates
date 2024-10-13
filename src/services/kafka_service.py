"""
kafka_service.py

Este módulo unifica la lógica para el productor y consumidor de Kafka.
"""

from confluent_kafka import Producer, KafkaError
from kafka import KafkaConsumer
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
            self.producer.flush()
            logger.info(
                "Todos los mensajes enviados, cerrando el productor de Kafka.")
        except KafkaError as e:
            logger.error(f"Error al cerrar el productor de Kafka: {e}")
            raise
        finally:
            logger.info("Productor de Kafka cerrado correctamente.")


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
                # Aquí puedes incluir la lógica para procesar el mensaje
                # por ejemplo, llamando a una función Flask o procesándolo localmente.
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
