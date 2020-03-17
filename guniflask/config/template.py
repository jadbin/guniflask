# coding=utf-8

from os.path import dirname, join

__all__ = ['_template_folder']

_template_folder = join(dirname(dirname(__file__)), 'templates')
