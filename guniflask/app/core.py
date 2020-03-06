# coding=utf-8

from flask import Flask

from guniflask.app.initializer import AppInitializer

__all__ = ['create_app']


def create_app(name):
    app = Flask(name)
    app_initializer = AppInitializer(app)
    app_initializer.init()
    return app
