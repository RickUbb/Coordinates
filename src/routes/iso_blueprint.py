"""
iso_blueprint.py

Este archivo define las rutas relacionadas con la obtención de códigos ISO de países. 
Proporciona una ruta GET que recibe como parámetro el nombre de un país y devuelve 
los códigos ISO correspondientes (alpha-2, alpha-3 y el código numérico). La ruta permite 
acceder a esta información a través de una solicitud HTTP GET.

Se utiliza Flask para manejar las rutas y Flask-CORS para permitir solicitudes CORS si es necesario.
"""

from flask import Blueprint, jsonify, request
# Para habilitar CORS en la ruta si es necesario
from flask_cors import cross_origin
from src.services.iso_service import get_iso_from_country

# Crear un blueprint de Flask para las rutas relacionadas con códigos ISO
main = Blueprint('iso_blueprint', __name__)


@cross_origin  # Permitir solicitudes desde otros orígenes (CORS)
@main.route('/', methods=['GET'])
def get_iso_codes():
    """
    Ruta GET para obtener los códigos ISO de un país.

    Se espera un parámetro de consulta 'country' en la URL. 
    Si el parámetro está presente, se llama a la función de servicio `get_iso_from_country`
    para obtener los códigos ISO (alpha-2, alpha-3 y numérico) correspondientes al país.

    Returns:
        JSON: Un objeto JSON que contiene los códigos ISO del país o un mensaje de error
              si el parámetro 'country' no fue proporcionado o si ocurrió un error en la búsqueda.
    """
    # Obtener el valor del parámetro 'country' de la solicitud GET
    country = request.args.get('country')

    # Validar que el parámetro 'country' esté presente en la solicitud
    if not country:
        return jsonify({'error': 'Country parameter is required'}), 400

    # Llamar a la función de servicio para obtener los códigos ISO del país
    result = get_iso_from_country(country)

    # Si no hay errores en la búsqueda, devolver los resultados con código 200
    # Si hay un error en la búsqueda, devolver el error con código 500
    return jsonify(result), 200 if 'error' not in result else 500
