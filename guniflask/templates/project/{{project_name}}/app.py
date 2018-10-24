# coding=utf-8

import logging
from importlib import import_module

from flask import Flask, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from guniflask.config import Config
from guniflask.utils.config import walk_modules
from guniflask.utils.logging import redirect_app_logger, redirect_logger
from guniflask.model import wrap_model
from guniflask.security import JwtAuthManager

log = logging.getLogger(__name__)

config = Config()

db = SQLAlchemy()
wrap_model(db.Model)

jwt_manager = JwtAuthManager()

app_default_settings = {
    'debug': False,
    'cors': True,
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}


def set_app_config(app):
    config.init_app(app)
    s = config.app_settings(app)
    for k, v in app_default_settings.items():
        s.setdefault(k, v)

    try:
        hooks = import_module(app.name + '.hooks')
    except ImportError:
        pass
    else:
        _make_settings = getattr(hooks, 'make_settings', None)
        if _make_settings:
            _make_settings(app, s)

    for k, v in s.items():
        if k.isupper():
            app.config[k] = v

    log.info('%s active profiles: %s', app.name, s['active_profiles'])


def init_app(app):
    s = config.app_settings(app)

    # CORS
    if s['cors']:
        if isinstance(s['cors'], dict):
            CORS(app, **s['cors'])
        else:
            CORS(app)

    # database configuration
    if 'SQLALCHEMY_DATABASE_URI' in app.config:
        db.init_app(app)

    # authentication
    jwt_manager.init_app(app)

    try:
        hooks = import_module(app.name + '.hooks')
    except ImportError:
        pass
    else:
        _init_app = getattr(hooks, 'init_app', None)
        if _init_app:
            _init_app(app, s)


def register_blueprints(app):
    def iter_blueprints():
        for module in walk_modules(app.name):
            for obj in vars(module).values():
                if isinstance(obj, Blueprint):
                    yield obj

    for b in iter_blueprints():
        app.register_blueprint(b)


def create_app(name):
    app = Flask(name)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    redirect_app_logger(app, gunicorn_logger)
    redirect_logger(name, gunicorn_logger)
    register_blueprints(app)
    set_app_config(app)
    init_app(app)
    return app
