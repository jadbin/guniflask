# coding=utf-8

from guniflask.app.initializer import AppInitializer


def create_app(name, settings=None, with_context=True):
    app_initializer = AppInitializer(name, app_settings=settings)
    app = app_initializer.init(with_context=with_context)
    return app
