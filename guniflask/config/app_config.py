# coding=utf-8

import os
import logging
from os.path import isfile, join
import copy
from collections import MutableMapping
from importlib import import_module

from flask import current_app
from werkzeug.local import LocalProxy
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from guniflask.model.wrapper import wrap_model
from guniflask.security.jwt import JwtManager

log = logging.getLogger(__name__)

__all__ = ['settings', 'app_default_settings',
           'AppConfig', 'load_config', 'load_profile_config',
           'Settings']

settings = LocalProxy(lambda: current_app.extensions['settings'])


class S:
    DEBUG = 'debug'
    CORS = 'cors'
    JWT = 'jwt'
    WRAP_SQLALCHEMY_MODEL = 'wrap_sqlalchemy_model'


app_default_settings = {
    S.DEBUG: False,
    S.CORS: True,
    S.JWT: False,
    S.WRAP_SQLALCHEMY_MODEL: True,
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}


class AppConfig:
    def __init__(self, app):
        s = Settings(self._load_app_settings(app.name))
        self._set_default_settings(s)
        app.extensions['settings'] = s
        self.app = app

    def init_app(self):
        app_module = import_module(self.app.name + '.app')
        s = self.app_settings(self.app)

        for k, v in s.items():
            if k.isupper():
                self.app.config[k] = v

        # CORS
        if s[S.CORS]:
            cors = s[S.CORS]
            if isinstance(cors, dict):
                CORS(self.app, **s[cors])
            else:
                CORS(self.app)

        # database configuration
        if s[S.WRAP_SQLALCHEMY_MODEL]:
            for v in vars(app_module).values():
                if isinstance(v, SQLAlchemy):
                    wrap_model(v.Model)

        # authentication
        if s[S.JWT]:
            jwt_manager = JwtManager()
            jwt_manager.init_app(self.app)

    @property
    def settings(self):
        return self.app_settings(current_app)

    def app_settings(self, app):
        return app.extensions['settings']

    def _load_app_settings(self, app_name):
        c = {}
        conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
        active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES')
        kwargs = self._get_default_settings_from_env()
        if conf_dir:
            c = load_profile_config(conf_dir, app_name, profiles=active_profiles, **kwargs)
            c['active_profiles'] = active_profiles
        c.update(kwargs)
        s = {}
        for name in c:
            if not name.startswith('_'):
                s[name] = c[name]
        return s

    def _get_default_settings_from_env(self):
        kwargs = {'home': os.environ.get('GUNIFLASK_HOME', os.curdir),
                  'project_name': os.environ.get('GUNIFLASK_PROJECT_NAME')}
        if os.environ.get('GUNIFLASK_DEBUG'):
            kwargs['debug'] = True
        else:
            kwargs['debug'] = False
        return kwargs

    def _set_default_settings(self, s):
        for k, v in app_default_settings.items():
            s.setdefault(k, v)


def load_config(fname, **kwargs):
    if fname is None or not isfile(fname):
        raise FileNotFoundError("Cannot find configuration file '{}'".format(fname))
    code = compile(open(fname, 'rb').read(), fname, 'exec')
    cfg = {
        "__builtins__": __builtins__,
        "__name__": "__config__",
        "__file__": fname,
        "__doc__": None,
        "__package__": None
    }
    cfg.update(kwargs)
    exec(code, cfg, cfg)
    return cfg


def load_profile_config(conf_dir, name, profiles=None, **kwargs):
    pc = load_config(join(conf_dir, name + '.py'), **kwargs)
    if profiles:
        profiles = profiles.split(',')
        profiles.reverse()
        for profile in profiles:
            if profile:
                pc_file = join(conf_dir, name + '_' + profile + '.py')
                if isfile(pc_file):
                    c = load_config(pc_file, **kwargs)
                    pc.update(c)
    return pc


class Settings(MutableMapping):
    def __init__(self, __values=None, **kwargs):
        self.attributes = {}
        self.update(__values, **kwargs)

    def __getitem__(self, name):
        if name not in self:
            return None
        return self.attributes[name]

    def __contains__(self, name):
        return name in self.attributes

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    def getbool(self, name, default=None):
        v = self.get(name, default)
        return getbool(v)

    def getint(self, name, default=None):
        v = self.get(name, default)
        return getint(v)

    def getfloat(self, name, default=None):
        v = self.get(name, default)
        return getfloat(v)

    def getlist(self, name, default=None):
        v = self.get(name, default)
        return getlist(v)

    def __setitem__(self, name, value):
        self.attributes[name] = value

    def set(self, name, value):
        self[name] = value

    def setdefault(self, k, default=None):
        if k not in self:
            self[k] = default

    def update(self, __values=None, **kwargs):
        if __values is not None:
            if isinstance(__values, Settings):
                for name in __values:
                    self[name] = __values[name]
            else:
                for name, value in __values.items():
                    self[name] = value
        for k, v in kwargs.items():
            self[k] = v

    def delete(self, name):
        del self.attributes[name]

    def __delitem__(self, name):
        del self.attributes[name]

    def copy(self):
        return copy.deepcopy(self)

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)


def getbool(v):
    try:
        return bool(int(v))
    except (ValueError, TypeError):
        if v in ("True", "true"):
            return True
        if v in ("False", "false"):
            return False
    return None


def getint(v):
    try:
        return int(v)
    except (ValueError, TypeError):
        pass
    return None


def getfloat(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        pass
    return None


def getlist(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.split(",")
    elif not hasattr(v, "__iter__"):
        v = [v]
    return list(v)
