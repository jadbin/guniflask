# coding=utf-8

import logging
from importlib import import_module
import inspect

from flask import Flask, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from guniflask.config import AppConfig
from guniflask.utils.logging import redirect_app_logger, redirect_logger
from guniflask.model import wrap_model
from guniflask.apidoc import ApiDoc
from guniflask.security.jwt import JwtManager
from guniflask.utils.env import walk_modules


class SETTINGS:
    DEBUG = 'debug'
    CORS = 'cors'
    JWT = 'jwt'
    WRAP_SQLALCHEMY_MODEL = 'wrap_sqlalchemy_model'
    API_DOC = 'apidoc'


app_default_settings = {
    SETTINGS.DEBUG: False,
    SETTINGS.CORS: True,
    SETTINGS.JWT: False,
    SETTINGS.WRAP_SQLALCHEMY_MODEL: True,
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}


def _get_app_module(app):
    return import_module(app.name + '.app')


def _get_instance_from_app(app, name):
    app_module = _get_app_module(app)
    obj = getattr(app_module, name, None)
    return obj


def set_app_config(app):
    config = AppConfig()
    config.init_app(app)
    s = config.app_settings(app)
    for k, v in app_default_settings.items():
        s.setdefault(k, v)

    app_module = _get_app_module(app)
    _make_settings = getattr(app_module, 'make_settings', None)
    if _make_settings:
        _make_settings(app, s)

    for k, v in s.items():
        if k.isupper():
            app.config[k] = v


def init_app(app):
    s = app.extensions['settings']
    app_module = _get_app_module(app)

    # CORS
    if s[SETTINGS.CORS]:
        cors = SETTINGS.CORS
        if isinstance(cors, dict):
            CORS(app, **s[cors])
        else:
            CORS(app)

    # database configuration
    if s[SETTINGS.WRAP_SQLALCHEMY_MODEL]:
        for v in vars(app_module):
            if isinstance(v, SQLAlchemy):
                wrap_model(v.Model)

    # authentication
    if s[SETTINGS.JWT]:
        jwt_manager = JwtManager()
        jwt_manager.init_app(app)

    # API doc
    if s[SETTINGS.API_DOC] or (s[SETTINGS.API_DOC] is None and s[SETTINGS.DEBUG]):
        apidoc = ApiDoc()
        apidoc.init_app(app)

    _init_app = getattr(app_module, 'init_app', None)
    if _init_app:
        _init_app(app, s)


def create_app(name):
    app = Flask(name)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    redirect_app_logger(app, gunicorn_logger)
    redirect_logger(name, gunicorn_logger)
    set_app_config(app)
    init_app(app)
    with app.app_context():
        register_blueprints(app)
    return app


def register_blueprints(app):
    registered_blueprints = set()

    def iter_blueprints():
        for module in walk_modules(app.name):
            for obj in vars(module).values():
                if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                    yield obj
                    registered_blueprints.add(obj)
                # FIXME: blueprint and route
                if inspect.isclass(obj) and obj.__module__ == module.__name__ and hasattr(obj, '__is_blueprint'):
                    b = Blueprint(obj.__name__, obj.__module__, **getattr(obj, '__options'))
                    o = obj()
                    for k in dir(o):
                        f = getattr(o, k)
                        if hasattr(f, '__is_route'):
                            b.add_url_rule(getattr(f, '__rule'), endpoint=f.__name__, view_func=f,
                                           **getattr(f, '__options'))
                    yield b

    for b in iter_blueprints():
        app.register_blueprint(b)

    del registered_blueprints
