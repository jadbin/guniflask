# coding=utf-8

from os.path import isfile, join
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


def load_profile_config(conf_dir, name, profile=None):
    pc = {}
    if profile:
        pc_file = join(conf_dir, name + '-' + profile + '.py')
        if not isfile(pc_file):
            pc_file = join(conf_dir, name + '_' + profile + '.py')
        if isfile(pc_file):
            pc = load_config(pc_file)
        else:
            raise FileNotFoundError("Cannot find the {} config in '{}' for profile: {}"
                                    .format(name, conf_dir, profile))
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
