# coding=utf-8

from guniflask.utils.template import *


def test_string_camelcase():
    assert string_camelcase('ABc-dE FgH') == 'AbcDeFgh'


def test_string_lowercase_hyphen():
    assert string_lowercase_hyphen(' AB_cD-Ef gh ') == 'ab-cd-ef-gh'


def test_string_lowercase_underscore():
    assert string_lowercase_underscore(' AB_cD-Ef gh ') == 'ab_cd_ef_gh'


def test_string_uppercase_underscore():
    assert string_uppercase_underscore(' AB_cD-Ef gh ') == 'AB_CD_EF_GH'
