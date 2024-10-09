"""
__init__.py

Este archivo inicializa la aplicación Flask y registra los blueprints. 
También habilita el soporte de CORS para permitir solicitudes desde dominios externos.
"""

from flask import Flask  # Importa la clase Flask
# Importa CORS para permitir el intercambio de recursos de origen cruzado
from flask_cors import CORS
# Importa las rutas del módulo CoordinatesRoutes
from src.routes import CoordinatesRoutes
# Importa las rutas del módulo IsoRoiso_blueprint
from src.routes import iso_blueprint

# Instancia la aplicación Flask
app = Flask(__name__)

# Aplica CORS para permitir solicitudes de diferentes dominios
CORS(app)


def init_app():
    """
    Inicializa la aplicación Flask y registra los blueprints.

    Returns:
        Flask: Instancia de la aplicación Flask con los blueprints registrados.
    """
    try:
        # Registra el blueprint del módulo CoordinatesRoutes bajo el prefijo '/coordinates'
        app.register_blueprint(CoordinatesRoutes.main,
                               url_prefix='/coordinates')

        # Registra el blueprint del módulo IsoRoutes bajo el prefijo '/iso'
        app.register_blueprint(iso_blueprint.main,
                               url_prefix='/iso')

        return app  # Devuelve la instancia de Flask configurada
    except Exception as e:
        # Manejo de errores en caso de fallo al registrar rutas o inicializar la app
        raise RuntimeError(
            f"Error al registrar las rutas en la aplicación Flask: {e}")
