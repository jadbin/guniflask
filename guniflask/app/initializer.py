# coding=utf-8

from importlib import import_module

from flask import Blueprint

from guniflask.config.app_config import AppConfig
from guniflask.utils.traversal import walk_modules
from guniflask.web.context import WebApplicationContext

__all__ = ['AppInitializer']


class AppInitializer:
    def __init__(self, app, app_settings=None):
        self.app = app
        self.config = AppConfig(self.app, app_settings=app_settings)

    def init(self):
        self._make_settings()
        bean_context = WebApplicationContext(self.app)
        self.app.bean_context = bean_context  # register bean context for app
        self._init_app()
        with self.app.app_context():
            self._register_blueprints()
            bean_context.scan(self.config.settings['project_name'])
            self._refresh_bean_context(bean_context)

    def _make_settings(self):
        app_module = self._get_app_module()
        _make_settings = getattr(app_module, 'make_settings', None)
        if _make_settings:
            s = self.config.settings
            _make_settings(self.app, s)

    def _init_app(self):
        self.config.init_app()
        app_module = self._get_app_module()
        _init_app = getattr(app_module, 'init_app', None)
        if _init_app:
            s = self.config.settings
            _init_app(self.app, s)

    def _refresh_bean_context(self, bean_context: WebApplicationContext):
        bean_context.refresh()

    def _register_blueprints(self):
        """
        Register declared Blueprint
        """
        registered_blueprints = set()

        def iter_blueprints():
            for module in walk_modules(self.config.settings['project_name']):
                for obj in vars(module).values():
                    if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                        yield obj
                        registered_blueprints.add(obj)

        for b in iter_blueprints():
            self.app.register_blueprint(b)

        del registered_blueprints

    def _get_app_module(self):
        return import_module(self.config.settings['project_name'] + '.app')
