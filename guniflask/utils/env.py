# coding=utf-8

import os
from os.path import isfile, join, isdir
from importlib import import_module
from pkgutil import iter_modules
import sys
import json
import re


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


project_name_regex = re.compile(r'[a-zA-Z\-]+')


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
    candidates = []
    for d in os.listdir(home_dir):
        if project_name_regex.fullmatch(d) and isfile(join(home_dir, d, '__init__.py')) \
                and isfile(join(home_dir, d, 'app.py')):
            candidates.append(d)
    if len(candidates) == 0:
        raise RuntimeError('Cannot infer the project nam')
