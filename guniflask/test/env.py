import os
from os.path import dirname, curdir, join, exists, abspath

from guniflask.config.env import load_app_env


def set_test_env():
    home = os.environ.get('GUNIFLASK_HOME')
    if home is None:
        home = abspath(curdir)
        while True:
            if not exists(join(home, '__init__.py')):
                break
            home = dirname(home)
        os.environ['GUNIFLASK_HOME'] = home
    os.environ.setdefault('GUNIFLASK_DEBUG', '1')
    os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'dev')
    load_app_env()
