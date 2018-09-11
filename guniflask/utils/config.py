# coding=utf-8

import os
from os.path import isfile, join, isdir, abspath
from importlib import import_module
from pkgutil import iter_modules
import inspect
import copy
from collections import MutableMapping


def load_config(fname):
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
    exec(code, cfg, cfg)
    return cfg


def load_profile_config(conf_dir, name, profiles=None):
    pc = {}
    if profiles:
        profiles = profiles.split(',')
        profiles.reverse()
        for profile in profiles:
            if profile:
                pc_file = join(conf_dir, name + '-' + profile + '.py')
                if not isfile(pc_file):
                    pc_file = join(conf_dir, name + '_' + profile + '.py')
                if isfile(pc_file):
                    c = load_config(pc_file)
                    pc.update(c)
    return pc


app_default_settings = {
    'active_profiles': None,
    'debug': False,
    'cors': True,
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}


def load_app_config(name):
    c = app_default_settings
    conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
    if conf_dir:
        c.update(load_config(join(conf_dir, name + '.py')))
        active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES', c.get('active_profiles'))
        c.update(load_profile_config(conf_dir, name, profiles=active_profiles))
        c['active_profiles'] = active_profiles
    settings = Settings()
    for name in c:
        if not name.startswith('_') and not inspect.ismodule(c[name]) and not inspect.isfunction(c[name]):
            settings[name] = c[name]
    if os.environ.get('GUNIFLASK_DEBUG'):
        settings['debug'] = True
    return settings


def walk_modules(path):
    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def walk_files(path):
    path = abspath(path)
    files = []
    if isdir(path):
        names = os.listdir(path)
        for name in names:
            files += walk_files(join(path, name))
    elif isfile(path):
        files.append(path)
    return files


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

    def update(self, values):
        if values is not None:
            if isinstance(values, Settings):
                for name in values:
                    self.set(name, values[name])
            else:
                for name, value in values.items():
                    self.set(name, value)

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
