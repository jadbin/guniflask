# coding=utf-8

import datetime as dt

import sqlalchemy


def model_to_dict(model):
    col_attrs = sqlalchemy.inspect(model).mapper.column_attrs
    d = {c.key: getattr(model, c.key) for c in col_attrs}
    # set tzinfo for datetime
    tz_info = dt.datetime.now(tz=dt.timezone.utc).astimezone().tzinfo
    for k, v in d.items():
        if isinstance(v, dt.datetime) and v.tzinfo is None:
            d[k] = v.replace(tzinfo=tz_info)
    return d


def dict_to_model(dict_obj, model_cls=None):
    if model_cls is None:
        return dict(dict_obj)
    col_attrs = sqlalchemy.inspect(model_cls).mapper.column_attrs
    kwargs = {c.key: dict_obj[c.key] for c in col_attrs if c.key in dict_obj}
    model = model_cls(**kwargs)
    return model


def update_model_by_dict(model, dict_obj):
    col_attrs = sqlalchemy.inspect(model).mapper.column_attrs
    for c in col_attrs:
        if c.key in dict_obj:
            setattr(model, c.key, dict_obj[c.key])
