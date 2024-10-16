"""
Este archivo implementa un consumidor Kafka que escucha mensajes en el tópico 'coordinates_topic'.
Cada mensaje es un conjunto de coordenadas y datos geográficos, que se deserializan desde formato JSON
y luego se envían a una API para su procesamiento posterior. La API espera recibir los datos en formato JSON.

Funciones:
    - consume_coordinates: Función principal que consume mensajes desde Kafka, los deserializa y los envía a una API.
"""

# Importamos la librería de Kafka para trabajar con el consumidor
from confluent_kafka import Consumer

# Librería para hacer peticiones HTTP a la API
import requests

# Librería para manejar variables de entorno
import os

# Librería para deserializar y manejar JSON
import json

# Definimos el nombre del tópico de Kafka del cual se van a consumir los mensajes
KAFKA_TOPIC = 'coordinates_topic'

# Definimos el servidor Kafka desde el cual se va a consumir, usando una variable de entorno, si no está definida usa 'localhost:9092'
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

# Definimos el endpoint de la API donde se enviarán los datos recibidos desde Kafka
API_ENDPOINT = 'http://localhost:5000/coordinates'

# Configuración del consumidor de Kafka
# Se define el servidor de Kafka, el grupo de consumidores al que pertenece y que inicie desde el primer mensaje disponible si es nuevo
consumer = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,  # Dirección del servidor de Kafka
    # Grupo de consumidores para que múltiples instancias trabajen juntas
    'group.id': 'coordinates_group',
    # Leer desde el principio si no hay un offset registrado
    'auto.offset.reset': 'earliest'
})

# Suscribimos el consumidor al tópico 'coordinates_topic'
consumer.subscribe([KAFKA_TOPIC])


def consume_coordinates():
    """
    Función principal que consume mensajes desde el tópico de Kafka, los deserializa y los envía a la API.
    Los mensajes se reciben en formato JSON y se espera que contengan una lista de objetos con coordenadas y otros datos.
    """

    # Ciclo infinito para consumir mensajes de Kafka de manera continua
    while True:
        # Esperar hasta 1 segundo para recibir un mensaje, si no recibe nada, devuelve None
        msg = consumer.poll(1.0)

        # Si no se recibió ningún mensaje, continuar con el siguiente ciclo
        if msg is None:
            continue

        # Si hubo un error al recibir el mensaje, imprimir el error y continuar con el siguiente ciclo
        if msg.error():
            print(f"Error en el mensaje: {msg.error()}")
            continue

        # Intentamos procesar el mensaje recibido
        try:
            # Decodificamos el valor del mensaje a una cadena UTF-8 (el mensaje llega en bytes)
            message_value = msg.value().decode('utf-8')
            print(f"Mensaje recibido: {message_value}")

            # Convertimos la cadena JSON en un objeto Python (lista de diccionarios)
            coordinates_data = json.loads(message_value)
            print(f"Datos deserializados: {coordinates_data}")

            # Enviamos los datos deserializados a la API usando una petición POST
            response = requests.post(
                API_ENDPOINT,  # URL de la API
                json=coordinates_data,  # Enviar los datos como JSON
                # Especificar el tipo de contenido como JSON
                headers={'Content-Type': 'application/json'}
            )

            # Verificamos si la respuesta de la API fue exitosa (código 200)
            if response.status_code == 200:
                print("Successfully sent coordinates to API")
            else:
                # Si la respuesta no fue exitosa, imprimimos el código de estado y el contenido de la respuesta
                print(f"Failed to send coordinates: {
                      response.status_code}, {response.text}")

        # Capturamos errores específicos si el mensaje JSON está mal formado
        except json.JSONDecodeError as e:
            print(f"Error al deserializar el mensaje JSON: {e}")

        # Capturamos cualquier otro tipo de error que ocurra durante la ejecución
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")


# Punto de entrada principal de la aplicación
if __name__ == "__main__":
    # Llamamos a la función para comenzar a consumir mensajes
    consume_coordinates()
