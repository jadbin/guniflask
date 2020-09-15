# coding=utf-8

from flask import Flask
from starlette.applications import Starlette
from starlette.middleware.wsgi import WSGIMiddleware

from guniflask.app.initializer import AppInitializer


def create_app(name, settings=None, with_context=True):
    app = Flask(name)
    app.asgi_app = Starlette()
    app_initializer = AppInitializer(app, app_settings=settings)
    app_initializer.init(with_context=with_context)
    app.asgi_app.mount('/', WSGIMiddleware(app))
    return app
