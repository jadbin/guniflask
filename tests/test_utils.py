# coding=utf-8

from guniflask import utils


def test_string_camelcase():
    assert utils.string_camelcase('ABc-dE FgH') == 'AbcDeFgh'


def test_string_lowercase_hyphen():
    assert utils.string_lowercase_hyphen(' AB_cD-Ef gh ') == 'ab-cd-ef-gh'


def test_string_lowercase_underscore():
    assert utils.string_lowercase_underscore(' AB_cD-Ef gh ') == 'ab_cd_ef_gh'


def test_string_uppercase_underscore():
    assert utils.string_uppercase_underscore(' AB_cD-Ef gh ') == 'AB_CD_EF_GH'
