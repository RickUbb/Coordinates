from flask import Flask
from flask_cors import CORS
from src.routes import CoordinatesRoutes

app = Flask(__name__)
CORS(app)


def init_app():

    app.register_blueprint(CoordinatesRoutes.main, url_prefix='/coordinates')

    return app
