# coding=utf-8

import sqlalchemy


def model_to_dict(model):
    col_attrs = sqlalchemy.inspect(model).mapper.column_attrs
    return {c.key: getattr(model, c.key) for c in col_attrs}


def dict_to_model(dict_obj, model_cls=None):
    if model_cls is None:
        return dict(dict_obj)
    col_attrs = sqlalchemy.inspect(model_cls).mapper.column_attrs
    kwargs = {c.key: dict_obj[c.key] for c in col_attrs if c.key in dict_obj}
    model = model_cls(**kwargs)
    return model
