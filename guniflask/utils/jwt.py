# coding=utf-8

import os


def generate_secret():
    return os.urandom(20).hex()
