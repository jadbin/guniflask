# coding=utf-8

from guniflask.app.initializer import AppInitializer


def create_app(with_context=True):
    app_initializer = AppInitializer()
    app = app_initializer.init(with_context=with_context)
    return app
