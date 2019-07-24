# coding=utf-8

import datetime as dt

import sqlalchemy


def model_to_dict(model, ignore=None):
    col_attrs = sqlalchemy.inspect(model).mapper.column_attrs
    d = {}
    tz_info = dt.datetime.now(tz=dt.timezone.utc).astimezone().tzinfo
    ignore_set = _get_ignore_set(ignore)
    for c in col_attrs:
        if c.key not in ignore_set:
            v = getattr(model, c.key)
            if isinstance(v, dt.datetime) and v.tzinfo is None:
                v = v.replace(tzinfo=tz_info)
            d[c.key] = v
    return d


def dict_to_model(dict_obj, model_cls=None, ignore=None):
    if model_cls is None:
        return dict(dict_obj)
    mapper = sqlalchemy.inspect(model_cls).mapper
    columns = mapper.columns
    col_attrs = mapper.column_attrs
    ignore_set = _get_ignore_set(ignore)
    kwargs = {}
    for c in col_attrs:
        if c.key in dict_obj and c.key not in ignore_set:
            v = dict_obj[c.key]
            if isinstance(columns[c.key].type, sqlalchemy.DateTime):
                v = string_to_datetime(v)
            kwargs[c.key] = v
    model = model_cls(**kwargs)
    return model


def update_model_by_dict(model, dict_obj, ignore=None):
    mapper = sqlalchemy.inspect(model).mapper
    columns = mapper.columns
    col_attrs = mapper.column_attrs
    ignore_set = _get_ignore_set(ignore)
    for c in col_attrs:
        if c.key in dict_obj and c.key not in ignore_set:
            v = dict_obj[c.key]
            if isinstance(columns[c.key].type, sqlalchemy.DateTime):
                v = string_to_datetime(v)
            setattr(model, c.key, v)


def string_to_datetime(s):
    if isinstance(s, int):
        return dt.datetime.fromtimestamp(s, tz=dt.timezone.utc).astimezone()
    elif isinstance(s, str):
        if 'GMT' in s:
            return dt.datetime.strptime(s, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=dt.timezone.utc).astimezone()
    return s


def _get_ignore_set(ignore):
    if isinstance(ignore, str):
        ignore = [i.strip() for i in ignore.split(',')]
    return set(ignore if ignore else [])


def wrap_model(model_cls):
    if not hasattr(model_cls, 'to_dict'):
        model_cls.to_dict = lambda self, **kwargs: model_to_dict(self, **kwargs)
    if not hasattr(model_cls, 'from_dict'):
        model_cls.from_dict = classmethod(lambda cls, dict_obj, **kwargs:
                                          dict_to_model(dict_obj, model_cls=cls, **kwargs))
    if not hasattr(model_cls, 'update_by_dict'):
        model_cls.update_by_dict = lambda self, dict_obj, **kwargs: update_model_by_dict(self, dict_obj, **kwargs)
    return model_cls
