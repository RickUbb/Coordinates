
# Aplicación de Coordenadas Geográficas

## Descripción

Esta aplicación automatiza el proceso de obtención y almacenamiento de coordenadas geográficas mediante la integración de APIs y procesamiento en tiempo real. Proporciona una solución eficiente para manejar datos de ubicación, normalizarlos y asegurarse de su precisión.

## Características

- **Automatización Eficiente**: Reduce el esfuerzo manual al automatizar la obtención de coordenadas geográficas precisas.
- **Integración de APIs**: Utiliza la API de OpenStreetMap (OSM) para obtener coordenadas y gestiona códigos ISO 3166-1 (alpha-2, alpha-3) mediante RestCountries y un archivo JSON local.
- **Procesamiento en Tiempo Real**: Implementa un consumidor Kafka para procesar mensajes en tiempo real y actualizar la base de datos MongoDB.
- **Validación y Normalización de Datos**: Asegura que los datos de ubicación sean consistentes, validando y normalizando los campos (country, province, city).
- **Gestión de Errores**: Los errores durante el procesamiento se manejan y almacenan en una colección específica de MongoDB (`coordinatesErrors`).
- **Portabilidad con Docker**: Facilita el despliegue en distintos entornos gracias a Docker, asegurando portabilidad y mínima configuración.

## Estructura de Datos

- **Entrada de API**: La API `/coordinates` acepta el siguiente formato:
  ```json
  {
    "city": "",
    "province": "Yaguate",
    "country": ""
  }


Mensajes Kafka: La estructura de los mensajes que procesa Kafka es la siguiente:

{"id": "508367781811056_66995527065be43ad58b7105","type": "dpt"}



-- TEST

LOCAL

docker exec -it kafka kafka-console-producer --topic to-enrich-lat-lon --bootstrap-server localhost:9092

{"id":"868457365374273","type":"dp"}
{"id":"535611435682501","type":"dp"}

{"id":"759309704255373_20241017","type":"insi"}

{"id":"490017610460731_66d61304528708ee2b86e354","type":"dpt"}

PROD

{"id":"508367781811056_66995527065be43ad58b7105","type":"dpt"}