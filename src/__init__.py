# Importa la clase Flask para crear una aplicación web.
from flask import Flask
# Importa CORS para manejar el Cross-Origin Resource Sharing (CORS).
from flask_cors import CORS
# Importa las rutas de coordenadas desde el módulo de rutas.
from src.routes import CoordinatesRoutes

# Crea una instancia de la aplicación Flask.
app = Flask(__name__)

# Aplica CORS a la aplicación para permitir solicitudes de diferentes dominios.
CORS(app)


def init_app():
    """
    Inicializa la aplicación Flask y registra los blueprints (rutas).

    Returns:
        app: Instancia de la aplicación Flask con las rutas registradas.
    """

    # Registra el blueprint del módulo CoordinatesRoutes en la ruta '/coordinates'.
    app.register_blueprint(CoordinatesRoutes.main, url_prefix='/coordinates')

    # Retorna la instancia de la aplicación Flask con el blueprint registrado.
    return app
