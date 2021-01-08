import getpass
import os
import tempfile
from importlib import import_module
from os.path import isfile, join, isdir, exists
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


def make_temp_dir(name: str):
    temp_dir = join(
        tempfile.gettempdir(),
        f'guniflask.{getpass.getuser()}',
        name,
    )
    if not exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    return temp_dir
