# coding=utf-8

import logging
from importlib import import_module
import inspect
import os
from os.path import isfile, join, dirname, exists
import multiprocessing

from flask import Flask, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from gunicorn.config import KNOWN_SETTINGS
from gunicorn.app.base import Application

from guniflask.config import AppConfig
from guniflask.utils.logging import redirect_app_logger, redirect_logger
from guniflask.model import wrap_model
from guniflask.apidoc import ApiDoc
from guniflask.security.jwt import JwtManager
from guniflask.utils.config import walk_modules, load_profile_config, walk_files
from guniflask.scheduling.background import BgProcessRunner


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


class GunicornApplication(Application):

    def __init__(self):
        self.options = self._make_options()
        super().__init__()

    def set_option(self, key, value):
        if key in self.cfg.settings:
            self.cfg.set(key, value)

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return create_app(_get_project_name())

    def _make_options(self):
        pid_dir = os.environ['GUNIFLASK_PID_DIR']
        log_dir = os.environ['GUNIFLASK_LOG_DIR']
        id_string = os.environ['GUNIFLASK_ID_STRING']
        project_name = _get_project_name()
        options = {
            'daemon': True,
            'preload_app': True,
            'workers': multiprocessing.cpu_count(),
            'worker_class': 'gevent',
            'pidfile': join(pid_dir, '{}-{}.pid'.format(project_name, id_string)),
            'accesslog': join(log_dir, '{}-{}.access.log'.format(project_name, id_string)),
            'errorlog': join(log_dir, '{}-{}.error.log'.format(project_name, id_string))
        }
        options.update(self._make_profile_options(os.environ.get('GUNIFLASK_ACTIVE_PROFILES')))
        # if debug
        if os.environ.get('GUNIFLASK_DEBUG'):
            options.update(self._make_debug_options())
        self._makedirs(options)
        # hook wrapper
        self._set_hook_wrapper(options)
        return options

    def _set_hook_wrapper(self, options):
        HookWrapper.from_config(options)

    def _make_profile_options(self, active_profiles):
        conf_dir = os.environ['GUNIFLASK_CONF_DIR']
        gc = load_profile_config(conf_dir, 'gunicorn', profiles=active_profiles)
        settings = {}
        snames = set([i.name for i in KNOWN_SETTINGS])
        for name in gc:
            if name in snames:
                settings[name] = gc[name]
        return settings

    @staticmethod
    def _make_debug_options():
        conf_dir = os.environ['GUNIFLASK_CONF_DIR']
        return {
            'accesslog': '-',
            'errorlog': '-',
            'loglevel': 'debug',
            'disable_redirect_access_to_syslog': True,
            'preload_app': False,
            'reload': True,
            'reload_extra_files': walk_files(conf_dir),
            'workers': 1,
            'daemon': False
        }

    @staticmethod
    def _makedirs(opts):
        for c in ['pidfile', 'accesslog', 'errorlog']:
            p = opts.get(c)
            if p:
                d = dirname(p)
                if d and not exists(d):
                    os.makedirs(d)


class HookWrapper:
    HOOKS = ['on_starting', 'on_reload', 'on_exit']

    def __init__(self, config, on_starting=None, on_reload=None, on_exit=None):
        self.config = config
        self._on_starting = on_starting
        self._on_reload = on_reload
        self._on_exit = on_exit

        project_name = _get_project_name()
        self._bg_process_runner = BgProcessRunner(project_name, config)

    @classmethod
    def from_config(cls, config):
        kw = {}
        for h in cls.HOOKS:
            kw[h] = config.get(h)
        wrapper = cls(config, **kw)
        for h in cls.HOOKS:
            config[h] = getattr(wrapper, h)
        return wrapper

    def on_starting(self, server):
        if self._on_starting is not None:
            self._on_starting(server)
        self._bg_process_runner.start()

    def on_reload(self, server):
        if self._on_reload is not None:
            self._on_reload(server)
        self._bg_process_runner.reload()

    def on_exit(self, server):
        if self._on_exit is not None:
            self._on_exit(server)
        self._bg_process_runner.stop()
