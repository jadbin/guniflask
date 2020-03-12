# coding=utf-8

import os
import logging
from os.path import isfile, join

from flask import current_app
from werkzeug.local import LocalProxy

from guniflask.config.setting import Settings

log = logging.getLogger(__name__)

__all__ = ['settings', 'SETTINGS', 'app_default_settings', 'AppConfig', 'load_config', 'load_profile_config']

settings = LocalProxy(lambda: current_app.extensions['settings'])


class SETTINGS:
    DEBUG = 'debug'
    CORS = 'cors'
    JWT = 'jwt'
    WRAP_SQLALCHEMY_MODEL = 'wrap_sqlalchemy_model'


app_default_settings = {
    SETTINGS.DEBUG: False,
    SETTINGS.CORS: True,
    SETTINGS.JWT: False,
    SETTINGS.WRAP_SQLALCHEMY_MODEL: True,
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}


class AppConfig:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        s = Settings(self._load_app_settings(app.name))
        self._set_default_settings(s)
        app.extensions['settings'] = s

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
