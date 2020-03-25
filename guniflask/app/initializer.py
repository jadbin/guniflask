# coding=utf-8

import logging
from importlib import import_module

from flask import Blueprint

from guniflask.utils.logging import redirect_app_logger, redirect_logger
from guniflask.config.app_config import AppConfig
from guniflask.utils.env import walk_modules
from guniflask.web.context import WebApplicationContext

__all__ = ['AppInitializer']


class AppInitializer:
    def __init__(self, app):
        self.app = app
        self.config = AppConfig(self.app)

    def init(self):
        self._configure_logger()
        self._make_settings()
        bean_context = self._create_bean_context()
        self.app.bean_context = bean_context  # register bean context for app
        self._init_app()
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

    def _make_settings(self):
        app_module = self._get_app_module()
        _make_settings = getattr(app_module, 'make_settings', None)
        if _make_settings:
            s = self.config.app_settings(self.app)
            _make_settings(self.app, s)

    def _init_app(self):
        self.config.init_app()
        app_module = self._get_app_module()
        _init_app = getattr(app_module, 'init_app', None)
        if _init_app:
            s = self.config.app_settings(self.app)
            _init_app(self.app, s)

    def _create_bean_context(self) -> WebApplicationContext:
        bean_context = WebApplicationContext(self.app)
        bean_context.scan(self.app.name)
        return bean_context

    def _refresh_bean_context(self, bean_context: WebApplicationContext):
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
