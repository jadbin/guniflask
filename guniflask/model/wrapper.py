# coding=utf-8

import datetime as dt

import sqlalchemy

__all__ = ['model_to_dict', 'result_to_dict', 'dict_to_model', 'update_model_by_dict', 'string_to_datetime',
           'wrap_model']


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


def string_to_datetime(s):
    if isinstance(s, int):
        return dt.datetime.fromtimestamp(s, tz=dt.timezone.utc).astimezone()
    elif isinstance(s, str):
        if 'GMT' in s:
            return dt.datetime.strptime(s, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=dt.timezone.utc).astimezone()
    return s


def _get_field_set(field):
    if isinstance(field, str):
        field = [i.strip() for i in field.split(',')]
    return set(field or [])


def wrap_model(model_cls):
    if not hasattr(model_cls, 'to_dict'):
        model_cls.to_dict = lambda self, **kwargs: model_to_dict(self, **kwargs)
    if not hasattr(model_cls, 'from_dict'):
        model_cls.from_dict = classmethod(lambda cls, dict_obj, **kwargs: dict_to_model(dict_obj, cls, **kwargs))
    if not hasattr(model_cls, 'update_by_dict'):
        model_cls.update_by_dict = lambda self, dict_obj, **kwargs: update_model_by_dict(self, dict_obj, **kwargs)
    if not hasattr(model_cls, 'result_to_dict'):
        model_cls.result_to_dict = classmethod(lambda cls, result, **kwargs: result_to_dict(result, cls, **kwargs))
    return model_cls
