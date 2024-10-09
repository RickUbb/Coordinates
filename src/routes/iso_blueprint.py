from flask import Blueprint, jsonify, request
# Importar la función de servicio
from src.services.iso_service import get_iso_from_country

main = Blueprint('iso_blueprint', __name__)


@main.route('/', methods=['GET'])
def get_iso_codes():
    country = request.args.get('country')
    if not country:
        return jsonify({'error': 'Country parameter is required'}), 400

    # Llamar a la función de servicio
    result = get_iso_from_country(country)
    return jsonify(result), 200 if 'error' not in result else 500
