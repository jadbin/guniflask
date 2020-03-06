# coding=utf-8

import os
from os.path import isfile, join, isdir
from importlib import import_module
from pkgutil import iter_modules


def walk_modules(path: str):
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


def walk_files(path: str):
    files = []
    if isdir(path):
        names = os.listdir(path)
        for name in names:
            files += walk_files(join(path, name))
    elif isfile(path):
        files.append(path)
    return files


def load_object(path):
    if isinstance(path, str):
        dot = path.rindex('.')
        module, name = path[:dot], path[dot + 1:]
        mod = import_module(module)
        return getattr(mod, name)
    return path
