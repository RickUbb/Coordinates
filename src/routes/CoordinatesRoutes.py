"""
CoordinatesRoutes.py

Este módulo define las rutas para obtener coordenadas geográficas utilizando Flask. 
La ruta principal permite recibir una solicitud con una lista de objetos que contienen el país, 
provincia y ciudad, y devuelve las coordenadas correspondientes si se encuentran en la base 
de datos o se consultan desde OpenStreetMap (OSM).
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
client = MongoClient(mongo['mongodb_url'])
database_name = client[mongo['mongodb_db_name']]
collection_name = mongo['mongodb_collection_name_coordinates']
collection_error_name = mongo["mongodb_collection_name_error_coordinates"]


@cross_origin
@main.route('/', methods=['POST'])
def get_coordinates():
    """
    Ruta POST para obtener coordenadas geográficas.
    Espera un JSON que contenga una lista de objetos, donde cada objeto tiene los campos:
    - country (subnivel_1)
    - province (subnivel_3)
    - city (subnivel_4)

    Returns:
        JSON: Un objeto que contiene las coordenadas de cada objeto enviado en la solicitud,
        o un mensaje de error si alguno de los objetos tiene parámetros inválidos.
    """
    try:
        # Obtener los datos del cuerpo de la solicitud en formato JSON
        data = request.get_json()
    except Exception as e:
        return jsonify({"error": f"No se pudo procesar el cuerpo de la solicitud. Asegúrate de que esté en formato JSON. Detalles del error: {str(e)}"}), 400

    # Verificar que el cuerpo de la solicitud sea una lista
    if not isinstance(data, list):
        return jsonify({"error": "El cuerpo de la solicitud debe ser una lista de objetos JSON."}), 400

    results = []  # Lista para almacenar los resultados de cada objeto
    errors = []   # Lista para almacenar errores de cada objeto

    # Procesar cada objeto en la lista
    for obj in data:
        # Normalizar los datos de entrada (país, provincia, ciudad)
        subnivel_1 = normalize(obj.get('country', 'NA')
                               ) if obj.get('country') else "NA"
        subnivel_3 = normalize(obj.get('province', 'NA')
                               ) if obj.get('province') else "NA"
        subnivel_4 = normalize(obj.get('city', 'NA')
                               ) if obj.get('city') else "NA"

        # Verificar si los parámetros requeridos están presentes
        if subnivel_3 == "NA" and subnivel_4 == "NA":
            errors.append({"error": f"Faltan parámetros en el objeto: {
                          obj}. Los campos 'province' o 'city' son obligatorios."})
            continue

        try:
            # Llamar a la función que busca o genera las coordenadas
            lat_prov, lon_prov, lat_city, lon_city = obtener_coordenadas(
                database_name, collection_name, collection_error_name, subnivel_1, subnivel_3, subnivel_4
            )

            # Si no se pudieron obtener las coordenadas, registrar el error
            if (not lat_prov or not lon_prov) and (not lat_city or not lon_city):
                errors.append(
                    {"error": f"No se encontraron coordenadas para el objeto: {obj}. Verifica que los nombres de 'province' y 'city' sean correctos."})
                continue
            elif subnivel_3 != "NA" and lat_prov is None and lon_prov is None:
                errors.append({"error": f"No se pudieron obtener coordenadas para la provincia '{
                              subnivel_3}' en el objeto: {obj}."})
            elif subnivel_4 != "NA" and lat_city is None and lon_city is None:
                errors.append({"error": f"No se pudieron obtener coordenadas para la ciudad '{
                              subnivel_4}' en el objeto: {obj}."})

            # Si las coordenadas fueron obtenidas correctamente, agregarlas a los resultados
            result = {}
            if subnivel_3 != "NA":
                result["lat_subnivel_3"] = lat_prov
                result["lon_subnivel_3"] = lon_prov
            if subnivel_4 != "NA":
                result["lat_subnivel_4"] = lat_city
                result["lon_subnivel_4"] = lon_city

            results.append(result)

        except Exception as e:
            errors.append(
                #    {"error": f"Error al procesar el objeto {obj}: {str(e)}"})
                {"error": f"Error al procesar el objeto {obj}. Ocurrió un problema al intentar obtener las coordenadas. Detalles del error: {str(e)}"})

            continue

    # Retornar los resultados y los errores
    return jsonify({
        "results": results,
        "errors": errors
    }), 200
