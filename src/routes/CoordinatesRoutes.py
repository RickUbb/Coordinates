"""
CoordinatesRoutes.py

Este módulo define las rutas para obtener coordenadas geográficas utilizando Flask. 
La ruta principal permite recibir una solicitud con los nombres del país, provincia y ciudad, 
y devuelve las coordenadas correspondientes si se encuentran en la base de datos o se consultan desde OpenStreetMap (OSM).
"""

# Flask y utilidades para manejar solicitudes y respuestas
from flask import Blueprint, request, jsonify
# Para permitir solicitudes CORS (Cross-Origin Resource Sharing)
from flask_cors import cross_origin
# Función para obtener coordenadas desde OSM o DB
from src.services.coordinates_api import obtener_coordenadas
# Función para normalizar texto
from src.utils.functions.normalize_text import normalize
from pymongo import MongoClient  # Para manejar la conexión con MongoDB
# Archivo de configuración para obtener los detalles de MongoDB
from config import mongo

# Crear un blueprint de Flask para las rutas relacionadas con las coordenadas
main = Blueprint('coordinates_blueprint', __name__)

# Configuración de cliente y conexión a la base de datos MongoDB
# Cliente MongoDB usando la URL de conexión
client = MongoClient(mongo['mongodb_url'])
database_name = client[mongo['mongodb_db_name']]  # Nombre de la base de datos
# Nombre de la colección donde se almacenan coordenadas
collection_name = mongo['mongodb_collection_name_coordinates']


@cross_origin  # Decorador para permitir solicitudes CORS en esta ruta
# Definir la ruta principal con el método POST
@main.route('/', methods=['POST'])
def get_coordinates():
    """
    Ruta POST para obtener coordenadas geográficas. Espera un JSON con los subniveles 1 (país), 
    3 (provincia) y 4 (ciudad). Si faltan parámetros o son inválidos, retorna un error.

    Returns:
        JSON: Las coordenadas de la provincia (subnivel_3) y la ciudad (subnivel_4), o un mensaje de error.
    """
    data = request.get_json()  # Obtener los datos del cuerpo de la solicitud en formato JSON

    # Normalizar los datos de entrada (país, provincia, ciudad)
    subnivel_1 = normalize(data['subnivel_1'])  # País
    subnivel_3 = normalize(data['subnivel_3'])  # Provincia
    subnivel_4 = normalize(data['subnivel_4'])  # Ciudad

    # Verificar si los parámetros requeridos están presentes
    if not subnivel_1 or not subnivel_3 or not subnivel_4:
        return jsonify({"error": "Faltan parámetros: subnivel_1, subnivel_3, subnivel_4 son requeridos"}), 400

    # Verificar si los valores de los subniveles son válidos
    if subnivel_1 == "NA" or subnivel_3 == "NA" or subnivel_4 == "NA":
        return jsonify({"error": "Faltan parámetros o son inconsistentes: subnivel_1, subnivel_3, subnivel_4 mal ingresados"}), 400

    # Llamar a la función que busca o genera las coordenadas
    lat_prov, lon_prov, lat_city, lon_city = obtener_coordenadas(
        database_name, collection_name, subnivel_1, subnivel_3, subnivel_4)

    # Si no se pudieron obtener las coordenadas, retornar un error de servidor
    if not lat_prov or not lon_prov or not lat_city or not lon_city:
        return jsonify({"error": "No se pudieron obtener las coordenadas"}), 500

    # Si las coordenadas fueron obtenidas correctamente, retornarlas en formato JSON
    return jsonify({
        "lat_subnivel_3": lat_prov,  # Latitud de la provincia
        "lon_subnivel_3": lon_prov,  # Longitud de la provincia
        "lat_subnivel_4": lat_city,  # Latitud de la ciudad
        "lon_subnivel_4": lon_city   # Longitud de la ciudad
    })
