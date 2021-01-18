import os
import re
import sys
from os.path import join, isfile, isdir

from dotenv import load_dotenv


def set_app_default_env():
    home_dir = os.environ.get('GUNIFLASK_HOME')
    if not home_dir:
        home_dir = os.getcwd()
        os.environ['GUNIFLASK_HOME'] = home_dir
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    if not os.environ.get('GUNIFLASK_CONF_DIR'):
        os.environ['GUNIFLASK_CONF_DIR'] = join(home_dir, 'conf')


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
    set_app_default_env()
    conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
    active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES')
    load_profile_env(conf_dir, active_profiles)


app_name_regex = re.compile(r'[a-zA-Z0-9_]+')


def infer_app_name(home_dir):
    candidates = []
    for d in os.listdir(home_dir):
        if app_name_regex.fullmatch(d) \
                and _find_py_module(join(home_dir, d), '__init__') \
                and _find_py_module(join(home_dir, d), 'app'):
            candidates.append(d)
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        raise RuntimeError(f'Cannot infer the app name, candidates: {candidates}')
    return candidates[0]


def _find_py_module(path, name):
    if not isdir(path):
        return False
    for s in os.listdir(path):
        if s.startswith(name) and (s.endswith('.py') or s.endswith('.so')):
            return True
    return False


def app_name_from_env():
    if not os.environ.get('GUNIFLASK_APP_NAME'):
        app_name = infer_app_name(os.environ.get('GUNIFLASK_HOME'))
        if app_name:
            os.environ['GUNIFLASK_APP_NAME'] = app_name
    return os.environ.get('GUNIFLASK_APP_NAME')
