# coding=utf-8

import os
import sys
from os.path import isfile, join, isdir
import json
import copy
from collections import MutableMapping

from flask import current_app
from werkzeug.local import LocalProxy

from guniflask.utils.config import load_profile_config

settings = LocalProxy(lambda: current_app.extensions['settings'])


class AppConfig:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        s = Settings(load_app_settings(app.name))
        app.extensions['settings'] = s

    @property
    def settings(self):
        return self.app_settings(current_app)

    def app_settings(self, app):
        return app.extensions['settings']


def load_app_settings(app_name):
    c = {}
    conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
    active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES')
    kwargs = get_default_settings_from_env()
    if conf_dir:
        c = load_profile_config(conf_dir, app_name, profiles=active_profiles, **kwargs)
        c['active_profiles'] = active_profiles
    c.update(kwargs)
    s = {}
    for name in c:
        if not name.startswith('_'):
            s[name] = c[name]
    return s


def get_default_settings_from_env():
    kwargs = {'home': os.environ.get('GUNIFLASK_HOME', os.curdir),
              'project_name': os.environ.get('GUNIFLASK_PROJECT_NAME')}
    if os.environ.get('GUNIFLASK_DEBUG'):
        kwargs['debug'] = True
    else:
        kwargs['debug'] = False
    return kwargs


def set_default_env():
    home_dir = os.environ.get('GUNIFLASK_HOME')
    if home_dir is None:
        home_dir = os.getcwd()
        os.environ['GUNIFLASK_HOME'] = home_dir
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    if 'GUNIFLASK_PROJECT_NAME' not in os.environ:
        project_name = infer_project_name(home_dir)
        if project_name:
            os.environ['GUNIFLASK_PROJECT_NAME'] = project_name
    if 'GUNIFLASK_CONF_DIR' not in os.environ:
        os.environ['GUNIFLASK_CONF_DIR'] = join(home_dir, 'conf')
    if 'GUNIFLASK_LOG_DIR' not in os.environ:
        os.environ['GUNIFLASK_LOG_DIR'] = join(home_dir, '.log')
    if 'GUNIFLASK_PID_DIR' not in os.environ:
        os.environ['GUNIFLASK_PID_DIR'] = join(home_dir, '.pid')
    if 'GUNIFLASK_ID_STRING' not in os.environ:
        os.environ['GUNIFLASK_ID_STRING'] = os.getlogin()


def get_project_name_from_env():
    return os.environ.get('GUNIFLASK_PROJECT_NAME')


def infer_project_name(home_dir):
    init_file = join(home_dir, '.guniflask-init.json')
    if isfile(init_file):
        try:
            with open(init_file, 'r') as f:
                data = json.load(f)
            project_name = data.get('project_name')
            if project_name and isdir(join(home_dir, project_name)):
                return project_name
        except Exception:
            pass
    for d in os.listdir(home_dir):
        if not d.startswith('.') and isfile(join(home_dir, d, 'app.py')):
            return d


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
