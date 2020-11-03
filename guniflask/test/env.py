# coding=utf-8

import os

from guniflask.config.env import set_app_default_env, load_app_env


def set_test_env():
    set_app_default_env()
    os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'dev')
    load_app_env()
