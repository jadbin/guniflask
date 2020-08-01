# coding=utf-8

import datetime as dt

import sqlalchemy

from guniflask.utils.instantiation import string_to_datetime

__all__ = ['model_to_dict', 'result_to_dict', 'dict_to_model', 'update_model_by_dict']


def model_to_dict(model, ignore=None, only=None, only_not_none=False):
    col_attrs = sqlalchemy.inspect(model).mapper.column_attrs
    d = {}
    tz_info = dt.datetime.now(tz=dt.timezone.utc).astimezone().tzinfo
    ignore_set = _get_field_set(ignore)
    only_set = _get_field_set(only)
    for c in col_attrs:
        if c.key not in ignore_set:
            if only and c.key not in only_set:
                continue
            v = getattr(model, c.key)
            if isinstance(v, dt.datetime) and v.tzinfo is None:
                v = v.replace(tzinfo=tz_info)
            if only_not_none and v is None:
                continue
            d[c.key] = v
    return d


def result_to_dict(result, model_cls, ignore=None, only=None, only_not_none=False):
    res = {}
    col_attrs = sqlalchemy.inspect(model_cls).mapper.column_attrs
    tz_info = dt.datetime.now(tz=dt.timezone.utc).astimezone().tzinfo
    ignore_set = _get_field_set(ignore)
    only_set = _get_field_set(only)
    for c in col_attrs:
        if c.key not in ignore_set:
            if only and c.key not in only_set:
                continue
            if hasattr(result, c.key):
                v = getattr(result, c.key)
                if isinstance(v, dt.datetime) and v.tzinfo is None:
                    v = v.replace(tzinfo=tz_info)
                if only_not_none and v is None:
                    continue
                res[c.key] = v
    return res


def dict_to_model(dict_obj, model_cls, ignore=None, only=None, only_not_none=False):
    mapper = sqlalchemy.inspect(model_cls).mapper
    columns = mapper.columns
    col_attrs = mapper.column_attrs
    ignore_set = _get_field_set(ignore)
    only_set = _get_field_set(only)
    kwargs = {}
    for c in col_attrs:
        if c.key in dict_obj and c.key not in ignore_set:
            if only and c.key not in only_set:
                continue
            v = dict_obj[c.key]
            if isinstance(columns[c.key].type, sqlalchemy.DateTime):
                v = string_to_datetime(v)
            if only_not_none and v is None:
                continue
            kwargs[c.key] = v
    model = model_cls(**kwargs)
    return model


def update_model_by_dict(model, dict_obj, ignore=None, only=None, only_not_none=False):
    mapper = sqlalchemy.inspect(model).mapper
    columns = mapper.columns
    col_attrs = mapper.column_attrs
    ignore_set = _get_field_set(ignore)
    only_set = _get_field_set(only)
    for c in col_attrs:
        if c.key in dict_obj and c.key not in ignore_set:
            if only and c.key not in only_set:
                continue
            v = dict_obj[c.key]
            if isinstance(columns[c.key].type, sqlalchemy.DateTime):
                v = string_to_datetime(v)
            if only_not_none and v is None:
                continue
            setattr(model, c.key, v)


def _get_field_set(field):
    if isinstance(field, str):
        field = [i.strip() for i in field.split(',')]
    return set(field or [])
