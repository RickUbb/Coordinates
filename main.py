"""
main.py

Este archivo es el punto de entrada principal de la aplicación Flask. Su función es inicializar la aplicación 
y ponerla en marcha cuando se ejecuta directamente. Se apoya en una función de inicialización que se encuentra 
en el módulo `src` para configurar correctamente la aplicación.
"""

from src import init_app  # Importa la función init_app desde el módulo src


def initialize_app():
    """
    Inicializa la aplicación Flask.

    Esta función es responsable de llamar a la función `init_app()` que se encuentra en el módulo `src`, 
    la cual devuelve una instancia configurada de la aplicación Flask.

    Returns:
        app (Flask): Instancia de la aplicación Flask inicializada.
    """
    app = init_app()  # Llama a la función init_app() para obtener la instancia de la app Flask
    return app  # Devuelve la app Flask inicializada


if __name__ == '__main__':
    """
    Este bloque se ejecuta solo si el archivo se ejecuta directamente (no si se importa como módulo).
    Aquí es donde se inicializa la app Flask y se ejecuta el servidor web de Flask.
    """
    app = initialize_app()  # Inicializa la aplicación Flask
    app.run(debug=True)  # Ejecuta la aplicación en el servidor local
