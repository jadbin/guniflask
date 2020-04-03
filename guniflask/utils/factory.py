# coding=utf-8

from importlib import import_module
from typing import get_type_hints, List, Collection, Any, Mapping, MutableMapping
import datetime as dt
import inspect
from collections import OrderedDict


def load_object(path):
    if isinstance(path, str):
        dot = path.rindex('.')
        module, name = path[:dot], path[dot + 1:]
        mod = import_module(module)
        return getattr(mod, name)
    return path


def string_to_datetime(s):
    if isinstance(s, int):
        return dt.datetime.fromtimestamp(s, tz=dt.timezone.utc).astimezone()
    elif isinstance(s, str):
        if 'GMT' in s:
            return dt.datetime.strptime(s, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=dt.timezone.utc).astimezone()
    return s


def instantiate_from_json(source, dtype: Any = None, target=None) -> Any:
    if isinstance(source, Mapping):
        if dtype is None:
            # inference type from target
            if target is not None:
                dtype = type(target)
        if dtype is None:
            # cannot instantiate without type
            return source

        type_hints = {} if dtype is None else get_type_hints(dtype)
        if target is None:
            target = dtype()

        if isinstance(target, MutableMapping):
            for k, v in source.items():
                target[k] = v
        else:
            for key in source:
                value = source[key]
                prop = getattr(target, key, None)
                prop_type = type_hints.get(key)

                prop_value = instantiate_from_json(value, dtype=prop_type, target=prop)
                if prop_value is not None:
                    setattr(target, key, prop_value)

            for key in type_hints:
                if not hasattr(target, key):
                    setattr(target, key, None)
        return target
    elif isinstance(source, List):
        if dtype is None:
            return source

        if issubclass(dtype, List):
            collection_type = list
        elif issubclass(dtype, Collection):
            collection_type = set
        else:
            collection_type = dtype

        element_type = None
        if hasattr(dtype, '__args__'):
            args = getattr(dtype, '__args__')
            if args is not None and len(args) == 1:
                element_type = args[0]

        result = []
        for v in source:
            result.append(instantiate_from_json(v, dtype=element_type))
        if collection_type is not None:
            result = collection_type(result)
        return result
    else:
        if dtype == dt.datetime:
            source = string_to_datetime(source)
        elif dtype is not None:
            try:
                source = dtype(source)
            except ValueError:
                pass
        return source


def inspect_args(func):
    signature = inspect.signature(func)
    paramters = signature.parameters
    return_type = signature.return_annotation

    hints = {}
    if return_type is not inspect._empty:
        hints['return'] = return_type

    args = OrderedDict()
    for p in paramters.values():
        args[p.name] = p.default
        if p.annotation is not inspect._empty:
            hints[p.name] = p.annotation

    return args, hints
