# coding=utf-8

import logging
from importlib import import_module

from flask import Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from guniflask.utils.logging import redirect_app_logger, redirect_logger
from guniflask.config.app_config import AppConfig, SETTINGS
from guniflask.model.wrapper import wrap_model
from guniflask.security.jwt import JwtManager
from guniflask.utils.env import walk_modules
from guniflask.web.context import AnnotationConfigWebApplicationContext

__all__ = ['AppInitializer']


class AppInitializer:
    def __init__(self, app):
        self.app = app

    def init(self):
        self._configure_logger()
        config = AppConfig()
        config.init_app(self.app)
        s = config.app_settings(self.app)
        self._make_settings(s)
        bean_context = self._create_bean_context()
        self.app.bean_context = bean_context  # register bean context for app
        self._init_app(config.app_settings(self.app))
        with self.app.app_context():
            self._register_blueprints()
            self._refresh_bean_context(bean_context)

    def _configure_logger(self):
        """
        Reuse gunicorn logger
        """
        gunicorn_logger = logging.getLogger('gunicorn.error')
        redirect_logger('guniflask', gunicorn_logger)
        redirect_app_logger(self.app, gunicorn_logger)
        redirect_logger(self.app.name, gunicorn_logger)

    def _make_settings(self, s):
        app_module = self._get_app_module()
        _make_settings = getattr(app_module, 'make_settings', None)
        if _make_settings:
            _make_settings(self.app, s)

        for k, v in s.items():
            if k.isupper():
                self.app.config[k] = v

    def _init_app(self, s):
        app_module = self._get_app_module()

        # CORS
        if s[SETTINGS.CORS]:
            cors = s[SETTINGS.CORS]
            if isinstance(cors, dict):
                CORS(self.app, **s[cors])
            else:
                CORS(self.app)

        # database configuration
        if s[SETTINGS.WRAP_SQLALCHEMY_MODEL]:
            for v in vars(app_module).values():
                if isinstance(v, SQLAlchemy):
                    wrap_model(v.Model)

        # authentication
        if s[SETTINGS.JWT]:
            jwt_manager = JwtManager()
            jwt_manager.init_app(self.app)

        _init_app = getattr(app_module, 'init_app', None)
        if _init_app:
            _init_app(self.app, s)

    def _create_bean_context(self) -> AnnotationConfigWebApplicationContext:
        bean_context = AnnotationConfigWebApplicationContext(self.app)
        bean_context.scan(self.app.name)
        return bean_context

    def _refresh_bean_context(self, bean_context: AnnotationConfigWebApplicationContext):
        bean_context.refresh()

    def _register_blueprints(self):
        """
        Register declared Blueprint
        """
        registered_blueprints = set()

        def iter_blueprints():
            for module in walk_modules(self.app.name):
                for obj in vars(module).values():
                    if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                        yield obj
                        registered_blueprints.add(obj)

        for b in iter_blueprints():
            self.app.register_blueprint(b)

        del registered_blueprints

    def _get_app_module(self):
        return import_module(self.app.name + '.app')

    def _get_instance_from_app(self, name):
        app_module = self._get_app_module()
        obj = getattr(app_module, name, None)
        return obj
