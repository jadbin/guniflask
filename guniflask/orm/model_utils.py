import datetime as dt

import sqlalchemy

from guniflask.utils.datatime import convert_to_datetime
from guniflask.utils.rule import make_ignore_rule_for_field, make_include_rule_for_field, make_only_rule_for_field


class DictRecursionError(Exception):
    pass


def model_to_dict(model, ignore=None, only=None, include=None):
    return _model_to_dict(model, ignore=ignore, only=only, include=include)


def _model_to_dict(model, ignore=None, only=None, include=None, __prefix='', __exists=None) -> dict:
    if __exists is None:
        __exists = set()
    if model in __exists:
        raise DictRecursionError
    __exists.add(model)
    mapper = sqlalchemy.inspect(model).mapper
    col_attrs = mapper.column_attrs
    relationships = mapper.relationships
    d = {}
    tz_info = dt.datetime.now().astimezone().tzinfo
    ignore_set = make_ignore_rule_for_field(ignore)
    only_set = make_only_rule_for_field(only)
    include_set = make_include_rule_for_field(include)
    keys = list(col_attrs.keys())
    for k in relationships.keys():
        if _new_prefix(__prefix, k) in include_set:
            keys.append(k)
    for key in keys:
        if _in_set(__prefix, key, ignore_set):
            continue
        if only and not _in_set(__prefix, key, only_set):
            continue

        if key in col_attrs:
            v = getattr(model, key)
            if isinstance(v, dt.datetime) and v.tzinfo is None:
                v = v.replace(tzinfo=tz_info)
            d[key] = v
        elif key in relationships:
            if not hasattr(model, key):
                continue
            v = getattr(model, key)
            try:
                if v:
                    if isinstance(v, (list, set)):
                        t = [
                            _model_to_dict(
                                obj,
                                ignore=ignore_set,
                                only=only_set,
                                include=include_set,
                                __prefix=_new_prefix(__prefix, key),
                                __exists=__exists,
                            )
                            for obj in v
                        ]
                        v = t
                    else:
                        v = _model_to_dict(
                            v,
                            ignore=ignore_set,
                            only=only_set,
                            include=include_set,
                            __prefix=_new_prefix(__prefix, key),
                            __exists=__exists,
                        )
                d[key] = v
            except DictRecursionError:
                pass
    __exists.remove(model)
    return d


def result_to_dict(result, ignore=None, only=None) -> dict:
    res = {}
    tz_info = dt.datetime.now().astimezone().tzinfo
    ignore_set = make_ignore_rule_for_field(ignore)
    only_set = make_only_rule_for_field(only)
    for key in result.keys():
        if key not in ignore_set:
            if only and key not in only_set:
                continue
            v = getattr(result, key)
            if isinstance(v, dt.datetime) and v.tzinfo is None:
                v = v.replace(tzinfo=tz_info)
            res[key] = v
    return res


def dict_to_model(dict_obj: dict, model_cls, ignore=None, only=None):
    return _dict_to_model(dict_obj, model_cls, ignore=ignore, only=only)


def _dict_to_model(dict_obj: dict, model_cls, ignore=None, only=None, __prefix=''):
    mapper = sqlalchemy.inspect(model_cls).mapper
    col_attrs = mapper.column_attrs
    relationships = mapper.relationships
    ignore_set = make_ignore_rule_for_field(ignore)
    only_set = make_only_rule_for_field(only)
    kwargs = {}
    for key in dict_obj:
        if key in col_attrs or key in relationships:
            if _in_set(__prefix, key, ignore_set):
                continue
            if only and not _in_set(__prefix, key, only_set):
                continue
            v = dict_obj[key]
            if key in relationships:
                if isinstance(v, dict):
                    obj_cls = relationships[key].mapper.class_
                    v = _dict_to_model(
                        v,
                        obj_cls,
                        ignore=ignore_set,
                        only=only_set,
                        __prefix=_new_prefix(__prefix, key),
                    )
                elif isinstance(v, (list, set)):
                    obj_cls = relationships[key].mapper.class_
                    t = [
                        _dict_to_model(
                            obj,
                            obj_cls,
                            ignore=ignore_set,
                            only=only_set,
                            __prefix=_new_prefix(__prefix, key),
                        )
                        for obj in v
                    ]
                    v = t
            elif key in col_attrs:
                if isinstance(getattr(model_cls, key).type, sqlalchemy.DateTime):
                    v = convert_to_datetime(v)
            kwargs[key] = v
    model = model_cls(**kwargs)
    return model


def update_model_by_dict(model, dict_obj: dict, ignore=None, only=None):
    _update_model_by_dict(model, dict_obj, ignore=ignore, only=only)


def _update_model_by_dict(model, dict_obj: dict, ignore=None, only=None, __prefix=''):
    mapper = sqlalchemy.inspect(model).mapper
    col_attrs = mapper.column_attrs
    relationships = mapper.relationships
    ignore_set = make_ignore_rule_for_field(ignore)
    only_set = make_only_rule_for_field(only)
    for key in dict_obj:
        if key in col_attrs or key in relationships:
            if _in_set(__prefix, key, ignore_set):
                continue
            if only and not _in_set(__prefix, key, only_set):
                continue
            v = dict_obj[key]
            if key in relationships:
                if isinstance(v, dict):
                    obj = getattr(model, key)
                    if obj:
                        _update_model_by_dict(
                            obj,
                            v,
                            ignore=ignore_set,
                            only=only_set,
                            __prefix=_new_prefix(__prefix, key),
                        )
                        v = obj
                    else:
                        obj_cls = relationships[key].mapper.class_
                        v = _dict_to_model(
                            v,
                            obj_cls,
                            ignore=ignore_set,
                            only=only_set,
                            __prefix=_new_prefix(__prefix, key),
                        )
                elif isinstance(v, (list, set)):
                    # FIXME
                    raise RuntimeError(f'do not support to update a list: "{_new_prefix(__prefix, key)}"')
            elif key in col_attrs:
                if isinstance(col_attrs[key].class_attribute.type, sqlalchemy.DateTime):
                    v = convert_to_datetime(v)
            setattr(model, key, v)


def _in_set(prefix: str, key: str, s: set):
    return _new_prefix(prefix, key) in s


def _new_prefix(prefix: str, key: str):
    if not prefix:
        return key
    return prefix + '.' + key
