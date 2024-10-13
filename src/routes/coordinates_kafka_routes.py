"""
coordinates_kafka_routes.py

Este módulo define las rutas Flask para integrar la API /coordinates con Kafka.
El productor publicará los datos y el consumidor los procesará utilizando Kafka.
"""

from flask import Blueprint, request, jsonify
from src.services.kafka_service import KafkaProducerService, KafkaConsumerService
import logging

# Crear un blueprint para las rutas de Kafka
kafka_routes = Blueprint('kafka_routes', __name__)

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialización del productor y consumidor de Kafka sin pasar parámetros
producer = KafkaProducerService()  # Ahora usa la configuración desde config.py
consumer = KafkaConsumerService()  # Inicialización del consumidor


@kafka_routes.route('/publish_coordinates', methods=['POST'])
def publish_coordinates():
    """
    Ruta para publicar un conjunto de coordenadas en el topic de Kafka.

    Returns:
        JSON: Confirmación de que los datos fueron publicados o un mensaje de error.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "El cuerpo de la solicitud no puede estar vacío."}), 400

        # Publicar el mensaje en Kafka
        producer.publish_message("coordinates", data)
        return jsonify({"message": "Coordenadas publicadas correctamente en Kafka."}), 200

    except Exception as e:
        logger.error(f"Error al publicar coordenadas en Kafka: {str(e)}")
        return jsonify({"error": f"No se pudieron publicar las coordenadas. Detalles: {str(e)}"}), 500


@kafka_routes.route('/consume_coordinates', methods=['GET'])
def consume_coordinates():
    """
    Ruta para consumir coordenadas desde Kafka y procesarlas.

    Returns:
        JSON: Mensaje de éxito o error.
    """
    try:
        # Iniciar el consumidor de Kafka
        consumer.consume_messages()
        return jsonify({"message": "Consumiendo coordenadas desde Kafka."}), 200

    except Exception as e:
        logger.error(f"Error al consumir coordenadas desde Kafka: {str(e)}")
        return jsonify({"error": f"No se pudieron consumir las coordenadas. Detalles: {str(e)}"}), 500
