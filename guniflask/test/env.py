# coding=utf-8

import os

from guniflask.config.env import load_app_env


def set_test_env():
    os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'dev')
    load_app_env()
