"""
main.py

Este archivo es el punto de entrada principal de la aplicación Flask. 
Se encarga de inicializar la aplicación y ejecutarla cuando se ejecuta directamente.
Depende de la función `init_app` que se encuentra en el módulo `src` para configurar 
correctamente la aplicación Flask.
"""

from src import init_app  # Importa la función init_app desde el módulo src

import sys


def initialize_app():
    """
    Inicializa la aplicación Flask.

    Esta función llama a `init_app()` para obtener una instancia configurada de Flask.

    Returns:
        Flask: Instancia inicializada de la aplicación Flask.
    """
    try:
        app = init_app()  # Llama a init_app() para obtener la instancia de la app
        return app
    except Exception as e:
        # Manejo básico de errores en caso de fallo en la inicialización
        raise RuntimeError(f"Error al inicializar la aplicación: {e}")


if __name__ == '__main__':
    """
    Este bloque se ejecuta solo si el archivo se ejecuta directamente, no si se importa como módulo.
    Se inicializa la aplicación Flask y se lanza el servidor local con modo de depuración activado.
    """
    try:
        app = initialize_app()  # Inicializa la aplicación Flask
        # Ejecuta la aplicación en modo debug (solo en desarrollo)
        app.run(host='0.0.0.0', port=5000, debug=False)  # Cambia aquí
    except Exception as e:
        print(f"Error al iniciar el servidor Flask: {
              e}", file=sys.stderr)  # Registrar error en stderr
