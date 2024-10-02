from src import init_app


def initialize_app():
    app = init_app()
    return app


if __name__ == '__main__':
    app = initialize_app()
    app.run()
