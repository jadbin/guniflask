# coding=utf-8

import datetime as dt

import sqlalchemy

from guniflask.utils.datatime import convert_to_datetime


class DictRecursionError(Exception):
    pass


def model_to_dict(model, ignore=None, only=None, max_depth=None, __prefix='', __exists=None) -> dict:
    if max_depth is not None:
        if max_depth <= 0:
            raise DictRecursionError
        max_depth -= 1
    if __exists is None:
        __exists = set()
    if model in __exists:
        raise DictRecursionError
    __exists.add(model)
    mapper = sqlalchemy.inspect(model).mapper
    col_attrs = mapper.column_attrs
    relationships = mapper.relationships
    d = {}
    tz_info = dt.datetime.now(tz=dt.timezone.utc).astimezone().tzinfo
    ignore_set = _ignore_set(ignore)
    only_set = _only_set(only)
    keys = list(col_attrs.keys()) + list(relationships.keys())
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
            v = getattr(model, key)
            try:
                if v:
                    if isinstance(v, (list, set)):
                        t = [
                            model_to_dict(
                                obj,
                                ignore=ignore_set,
                                only=only_set,
                                max_depth=max_depth,
                                __prefix=_new_prefix(__prefix, key),
                                __exists=__exists,
                            )
                            for obj in v
                        ]
                        v = t
                    else:
                        v = model_to_dict(
                            v,
                            ignore=ignore_set,
                            only=only_set,
                            max_depth=max_depth,
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
    tz_info = dt.datetime.now(tz=dt.timezone.utc).astimezone().tzinfo
    ignore_set = _ignore_set(ignore)
    only_set = _only_set(only)
    for key in result.keys():
        if key not in ignore_set:
            if only and key not in only_set:
                continue
            v = getattr(result, key)
            if isinstance(v, dt.datetime) and v.tzinfo is None:
                v = v.replace(tzinfo=tz_info)
            res[key] = v
    return res


def dict_to_model(dict_obj: dict, model_cls, ignore=None, only=None, __prefix=''):
    mapper = sqlalchemy.inspect(model_cls).mapper
    col_attrs = mapper.column_attrs
    relationships = mapper.relationships
    ignore_set = _ignore_set(ignore)
    only_set = _only_set(only)
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
                    v = dict_to_model(
                        v,
                        obj_cls,
                        ignore=ignore_set,
                        only=only_set,
                        __prefix=_new_prefix(__prefix, key),
                    )
                elif isinstance(v, (list, set)):
                    obj_cls = relationships[key].mapper.class_
                    t = [
                        dict_to_model(
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


def update_model_by_dict(model, dict_obj: dict, ignore=None, only=None, __prefix=''):
    mapper = sqlalchemy.inspect(model).mapper
    col_attrs = mapper.column_attrs
    relationships = mapper.relationships
    ignore_set = _ignore_set(ignore)
    only_set = _only_set(only)
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
                        update_model_by_dict(
                            obj,
                            v,
                            ignore=ignore_set,
                            only=only_set,
                            __prefix=_new_prefix(__prefix, key),
                        )
                        v = obj
                    else:
                        obj_cls = relationships[key].mapper.class_
                        v = dict_to_model(
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


def _to_set(field):
    if isinstance(field, str):
        field = [i.strip() for i in field.split(',')]
    return set(field or [])


def _ignore_set(field):
    if isinstance(field, set):
        return field
    return _to_set(field)


def _only_set(field):
    if isinstance(field, set):
        return field
    s = _to_set(field)
    for k in list(s):
        if '.' in k:
            t = k.split('.')
            for i in range(1, len(t)):
                s.add('.'.join(t[:i]))
    return s


def _in_set(prefix: str, key: str, s: set):
    return _new_prefix(prefix, key) in s


def _new_prefix(prefix: str, key: str):
    if not prefix:
        return key
    return prefix + '.' + key
