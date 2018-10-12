# coding=utf-8

import os
from os.path import join
import copy
from collections import MutableMapping

from guniflask.utils.config import load_config, load_profile_config


class Config:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        settings = Settings(self._load_app_config(app))
        app.extensions['settings'] = settings

    def _load_app_config(self, app):
        c = {}
        conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
        if conf_dir:
            c.update(load_config(join(conf_dir, app.name + '.py')))
            active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES')
            c.update(load_profile_config(conf_dir, app.name, profiles=active_profiles))
            c['active_profiles'] = active_profiles
        settings = {}
        for name in c:
            if not name.startswith('_'):
                settings[name] = c[name]
        if os.environ.get('GUNIFLASK_DEBUG'):
            settings['debug'] = True
        settings['home'] = os.environ.get('GUNIFLASK_HOME', os.curdir)
        return settings


class Settings(MutableMapping):
    def __init__(self, values=None):
        self.attributes = {}
        self.update(values)

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
        self.set(name, value)

    def set(self, name, value):
        self.attributes[name] = value

    def setdefault(self, k, default=None):
        if self[k] is None:
            self[k] = default

    def update(self, __values=None, **kwargs):
        if __values is not None:
            if isinstance(__values, Settings):
                for name in __values:
                    self.set(name, __values[name])
            else:
                for name, value in __values.items():
                    self.set(name, value)
        for k, v in kwargs.items():
            self.set(k, v)

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
