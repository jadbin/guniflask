# coding=utf-8

import os
from os.path import isfile, join, isdir, abspath
from importlib import import_module
from pkgutil import iter_modules
import inspect


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
    from guniflask.settings import Settings

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
