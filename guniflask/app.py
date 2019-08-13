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
from guniflask.apidoc import ApiDoc

log = logging.getLogger(__name__)

app_default_settings = {
    'debug': False,
    'cors': True,
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
    app_module = _get_app_module(app)
    config = _get_instance_from_app(app, 'config')
    assert isinstance(config, Config)

    config.init_app(app)
    s = config.app_settings(app)
    for k, v in app_default_settings.items():
        s.setdefault(k, v)

    _make_settings = getattr(app_module, 'make_settings', None)
    if _make_settings:
        _make_settings(app, s)

    for k, v in s.items():
        if k.isupper():
            app.config[k] = v

    log.info('%s active profiles: %s', app.name, s['active_profiles'])


def init_app(app):
    app_module = _get_app_module(app)
    config = _get_instance_from_app(app, 'config')
    assert isinstance(config, Config)

    s = config.app_settings(app)

    # CORS
    if s['cors']:
        if isinstance(s['cors'], dict):
            CORS(app, **s['cors'])
        else:
            CORS(app)

    # database configuration
    if 'SQLALCHEMY_DATABASE_URI' in app.config:
        db = _get_instance_from_app(app, 'db')
        assert isinstance(db, SQLAlchemy)
        wrap_model(db.Model)
        db.init_app(app)

    # authentication
    jwt_manager = _get_instance_from_app(app, 'jwt_manager')
    if isinstance(jwt_manager, JwtAuthManager):
        jwt_manager.init_app(app)

    # API doc
    if s['apidoc'] or (s['apidoc'] is None and s['debug']):
        apidoc = ApiDoc()
        apidoc.init_app(app)

    _init_app = getattr(app_module, 'init_app', None)
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


def create_bg_process_app(name):
    app = Flask(name)
    set_app_config(app)
    init_app(app)
    return app
