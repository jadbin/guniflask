# coding=utf-8

import re

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
