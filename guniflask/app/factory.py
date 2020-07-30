# coding=utf-8

from flask import Flask

from guniflask.app.initializer import AppInitializer

__all__ = ['create_app']


def create_app(name, settings=None):
    app = Flask(name)
    app_initializer = AppInitializer(app, app_settings=settings)
    app_initializer.init()
    return app
