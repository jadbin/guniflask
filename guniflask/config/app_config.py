# coding=utf-8

import logging
import copy
from collections import MutableMapping
from typing import Union

from flask import current_app
from werkzeug.local import LocalProxy

log = logging.getLogger(__name__)

__all__ = ['settings', 'Settings', 'AppConfig']


class AppConfig:
    def __init__(self, app, app_settings=None):
        if app_settings is None:
            self.settings = Settings()
        if not isinstance(app_settings, Settings):
            self.settings = Settings(app_settings)
        self.app = app

    def init_app(self):
        self.app.extensions['settings'] = self.settings
        for k, v in self.settings.items():
            if k.isupper():
                self.app.config[k] = v


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

    def get_by_prefix(self, prefix, default=None):
        s = prefix.split('.')
        obj = self
        for i in s:
            if hasattr(obj, i):
                obj = getattr(obj, i)
            elif hasattr(obj, '__getitem__') and hasattr(obj, '__contains__'):
                if i in obj:
                    obj = obj[i]
                else:
                    obj = None
            else:
                obj = None
            if obj is None:
                break
        if obj is None:
            return default
        return obj

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


settings: Union[LocalProxy, Settings] = LocalProxy(lambda: current_app.extensions['settings'])
