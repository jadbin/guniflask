# coding=utf-8

from importlib import import_module

from flask import Blueprint, Flask

from guniflask.config.app_settings import Settings
from guniflask.utils.path import walk_modules
from guniflask.web.context import WebApplicationContext


class AppInitializer:
    def __init__(self, name, app_settings=None):
        self.name = name
        if app_settings is None:
            self.settings = Settings()
        if not isinstance(app_settings, Settings):
            self.settings = Settings(app_settings)

    def init(self, with_context=True):
        app = Flask(self.name)
        self._make_settings(app)
        if with_context:
            bean_context = WebApplicationContext(app)
            app.bean_context = bean_context  # register bean context for app
        self._init_app(app)
        with app.app_context():
            self._register_blueprints(app)
            if with_context:
                app.bean_context.scan(self.settings['project_name'])
                self._refresh_bean_context(app.bean_context)
        return app

    def _make_settings(self, app):
        app_module = self._get_app_module()
        _make_settings = getattr(app_module, 'make_settings', None)
        if _make_settings:
            s = self.settings
            _make_settings(app, s)

    def _init_app(self, app):
        app.settings = self.settings
        for k, v in self.settings.items():
            if k.isupper():
                app.config[k] = v

        app_module = self._get_app_module()
        _init_app = getattr(app_module, 'init_app', None)
        if _init_app:
            s = self.settings
            _init_app(app, s)

    def _refresh_bean_context(self, bean_context: WebApplicationContext):
        bean_context.refresh()

    def _register_blueprints(self, app):
        """
        Register declared Blueprint
        """
        registered_blueprints = set()

        def iter_blueprints():
            for module in walk_modules(self.settings['project_name']):
                for obj in vars(module).values():
                    if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                        yield obj
                        registered_blueprints.add(obj)

        for b in iter_blueprints():
            app.register_blueprint(b)

        del registered_blueprints

    def _get_app_module(self):
        return import_module(self.settings['project_name'] + '.app')
