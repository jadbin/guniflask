# coding=utf-8

import os


def get_master_pid():
    return os.getppid()
