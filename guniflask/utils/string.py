import re

_camelcase_invalid_chars = re.compile(r'[^a-zA-Z\d]')

_camelcase_split_chars = re.compile(r'(.)([A-Z][a-z]+)')
_camelcase_split_chars2 = re.compile(r'([a-z0-9])([A-Z])')


def string_camelcase(s):
    a = _camelcase_invalid_chars.split(s)
    return ''.join([(i[0].upper() + i[1:]) for i in a if i])


def string_lowercase_hyphen(s):
    return string_lowercase_underscore(s).replace('_', '-')


def string_lowercase_underscore(s):
    s = string_camelcase(s)
    s = _camelcase_split_chars.sub(r'\1_\2', s)
    return _camelcase_split_chars2.sub(r'\1_\2', s).lower()


def string_uppercase_underscore(s):
    return string_lowercase_underscore(s).upper()


def comma_delimited_list_to_set(s):
    return set(comma_delimited_list_to_array(s))


def comma_delimited_list_to_array(s):
    return s.split(',')
