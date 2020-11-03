# coding=utf-8

import os
import re
import sys
from os.path import join, isfile

from dotenv import load_dotenv


def set_app_env():
    home_dir = os.environ.get('GUNIFLASK_HOME')
    if not home_dir:
        home_dir = os.getcwd()
        os.environ['GUNIFLASK_HOME'] = home_dir
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    if not os.environ.get('GUNIFLASK_CONF_DIR'):
        os.environ['GUNIFLASK_CONF_DIR'] = join(home_dir, 'conf')
    load_app_env()


def load_env(fname):
    if fname is None or not isfile(fname):
        raise FileNotFoundError(f"Cannot find env file '{fname}'")
    load_dotenv(fname)


def load_profile_env(conf_dir, profiles: str = None):
    base_file = join(conf_dir, 'app.env')
    if isfile(base_file):
        load_env(base_file)
    if profiles:
        profiles = profiles.split(',')
        for profile in reversed(profiles):
            if profile:
                p_file = join(conf_dir, f'app_{profile}.env')
                if isfile(p_file):
                    load_env(p_file)


def load_app_env():
    conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
    active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES')
    load_profile_env(conf_dir, active_profiles)


project_name_regex = re.compile(r'[a-z0-9_]+')


def infer_project_name(home_dir):
    candidates = []
    for d in os.listdir(home_dir):
        if project_name_regex.fullmatch(d) and isfile(join(home_dir, d, '__init__.py')) \
                and isfile(join(home_dir, d, 'app.py')):
            candidates.append(d)
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        raise RuntimeError(f'Cannot infer the project name, candidates: {candidates}')
    return candidates[0]


def app_name_from_env():
    if not os.environ.get('GUNIFLASK_PROJECT_NAME'):
        project_name = infer_project_name(os.environ.get('GUNIFLASK_HOME'))
        if project_name:
            os.environ['GUNIFLASK_PROJECT_NAME'] = project_name
    return os.environ.get('GUNIFLASK_PROJECT_NAME')