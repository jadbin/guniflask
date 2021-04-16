from importlib import import_module

from flask import Blueprint, Flask

from guniflask.config.app_settings import Settings
from guniflask.config.env import app_name_from_env
from guniflask.config.load_utils import load_app_settings
from guniflask.security_config.authentication_config import AuthenticationConfiguration
from guniflask.security_config.web_security_config import WebSecurityConfiguration
from guniflask.utils.path import walk_modules
from guniflask.web.context import WebApplicationContext
from guniflask.web.health_check import HealthCheckConfiguration
from guniflask.web.scheduling_config import WebAsyncConfiguration, WebSchedulingConfiguration


class AppInitializer:
    def __init__(self):
        self.name = app_name_from_env()
        app_settings = load_app_settings(self.name)
        self.settings = Settings(app_settings)

    def init(self, app=None, with_context=True):
        if app is None:
            app = Flask(self.name)
        self._make_settings(app)
        if with_context:
            self._create_bean_context(app)
        self._init_app(app)
        with app.app_context():
            self._register_blueprints(app)
            self._refresh_bean_context(app)
        return app

    def _make_settings(self, app):
        app_module = self._get_app_module()
        _make_settings = getattr(app_module, 'make_settings', None)
        if _make_settings:
            s = self.settings
            _make_settings(app, s)

    def _init_app(self, app):
        setattr(app, 'settings', self.settings)
        for k, v in self.settings.items():
            if k.isupper():
                app.config[k] = v

        app_module = self._get_app_module()
        _init_app = getattr(app_module, 'init_app', None)
        if _init_app:
            s = self.settings
            _init_app(app, s)

    def _create_bean_context(self, app):
        bean_context = WebApplicationContext(app)
        self._auto_configure_bean_context(bean_context)
        setattr(app, 'bean_context', bean_context)

    def _auto_configure_bean_context(self, bean_context: WebApplicationContext):
        bean_context.register(AuthenticationConfiguration)
        bean_context.register(WebSecurityConfiguration)
        bean_context.register(WebAsyncConfiguration)
        bean_context.register(WebSchedulingConfiguration)
        bean_context.register(HealthCheckConfiguration)

    def _refresh_bean_context(self, app):
        if hasattr(app, 'bean_context'):
            bean_context: WebApplicationContext = getattr(app, 'bean_context')
            bean_context.scan(self.settings['app_name'])
            bean_context.refresh()

    def _register_blueprints(self, app):
        """
        Register declared Blueprint
        """
        registered_blueprints = set()

        def iter_blueprints():
            for module in walk_modules(self.settings['app_name']):
                for obj in vars(module).values():
                    if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                        yield obj
                        registered_blueprints.add(obj)

        for b in iter_blueprints():
            app.register_blueprint(b)

        del registered_blueprints

    def _get_app_module(self):
        return import_module(self.settings['app_name'] + '.app')
