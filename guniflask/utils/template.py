# coding=utf-8

import re
from os.path import dirname, join

from jinja2 import Environment

from guniflask.errors import TemplateError

template_folder = join(dirname(dirname(__file__)), 'templates')

_camelcase_invalid_chars = re.compile(r'[^a-zA-Z\d]')

_name_invalid_chars = re.compile(r'[^a-zA-Z\d\-_]')


def string_camelcase(s):
    return _camelcase_invalid_chars.sub('', s.title())


def string_lowercase_hyphen(s):
    return _name_invalid_chars.sub('', s.strip().replace(' ', '-').lower()).replace('_', '-')


def string_lowercase_underscore(s):
    return _name_invalid_chars.sub('', s.strip().replace(' ', '_').lower()).replace('-', '_')


def string_uppercase_underscore(s):
    return _name_invalid_chars.sub('', s.strip().replace(' ', '_').upper()).replace('-', '_')


def _raise_helper(message):
    if message:
        raise TemplateError(message)
    raise TemplateError


def _assert_helper(logical, message=None):
    if not logical:
        _raise_helper(message)
    return ''


def jinja2_env():
    env = Environment(keep_trailing_newline=True)
    env.globals['raise'] = _raise_helper
    env.globals['assert'] = _assert_helper
    return env
