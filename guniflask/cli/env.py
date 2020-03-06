# coding=utf-8

import os
import sys
from os.path import join, isfile, isdir
import re
import json

__all__ = ['set_default_env', 'infer_project_name', 'get_project_name_from_env']


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


def get_project_name_from_env():
    return os.environ.get('GUNIFLASK_PROJECT_NAME')
