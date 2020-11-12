from guniflask.app.initializer import AppInitializer
from guniflask.config import load_app_env


def create_app(with_context=True):
    load_app_env()
    app_initializer = AppInitializer()
    app = app_initializer.init(with_context=with_context)
    return app
