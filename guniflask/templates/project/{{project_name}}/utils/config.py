# coding=utf-8

import os
from os.path import isfile, join, isdir, abspath
from importlib import import_module
from pkgutil import iter_modules


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
