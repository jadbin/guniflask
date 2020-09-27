# coding=utf-8

from flask import Flask

from guniflask.app.initializer import AppInitializer


def create_app(name, settings=None, with_context=True):
    app = Flask(name)
    app_initializer = AppInitializer(app, app_settings=settings)
    app_initializer.init(with_context=with_context)
    return app
