# coding=utf-8

import logging
from importlib import import_module
import inspect

from flask import Flask, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from guniflask.config import Config
from guniflask.utils.logging import redirect_app_logger, redirect_logger
from guniflask.model import wrap_model
from guniflask.apidoc import ApiDoc
from guniflask.security import JwtManager
from guniflask.utils.config import walk_modules

log = logging.getLogger(__name__)

app_default_settings = {
    'debug': False,
    'cors': True,
    'jwt': False,
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}

sqlalchemy_instances = []


def new_sqlalchemy(*args, **kwargs) -> SQLAlchemy:
    obj = SQLAlchemy(*args, **kwargs)
    sqlalchemy_instances.append(obj)
    return obj


def _get_app_module(app):
    return import_module(app.name + '.app')


def _get_instance_from_app(app, name):
    app_module = _get_app_module(app)
    obj = getattr(app_module, name, None)
    return obj


def set_app_config(app):
    config = Config()
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

    log.info('%s active profiles: %s', app.name, s['active_profiles'])


def init_app(app):
    s = app.extensions['settings']

    # CORS
    if s['cors']:
        if isinstance(s['cors'], dict):
            CORS(app, **s['cors'])
        else:
            CORS(app)

    # database configuration
    for db in sqlalchemy_instances:
        wrap_model(db.Model)

    # authentication
    if s['jwt']:
        jwt_manager = JwtManager()
        jwt_manager.init_app(app)

    # API doc
    if s['apidoc'] or (s['apidoc'] is None and s['debug']):
        apidoc = ApiDoc()
        apidoc.init_app(app)

    app_module = _get_app_module(app)
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
    def iter_blueprints():
        for module in walk_modules(app.name):
            for obj in vars(module).values():
                if isinstance(obj, Blueprint):
                    yield obj
                if inspect.isclass(obj) and hasattr(obj, '__is_blueprint'):
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


def create_bg_process_app(name):
    app = Flask(name)
    set_app_config(app)
    init_app(app)
    return app
