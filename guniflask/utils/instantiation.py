# coding=utf-8

from importlib import import_module
from typing import get_type_hints, List, Set, Any, Mapping, MutableMapping, Optional
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
    if source is None:
        return
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

        argc, etype = resolve_arg_type(dtype)

        if argc is ArgType.LIST:
            collection_type = list
        elif argc is ArgType.SET:
            collection_type = set
        else:
            assert inspect.isclass(dtype), 'Cannot convert a list to {}'.format(dtype)
            collection_type = dtype

        result = []
        for v in source:
            result.append(instantiate_from_json(v, dtype=etype))
        if collection_type is not None:
            result = collection_type(result)
        return result
    else:
        if dtype == dt.datetime:
            source = string_to_datetime(source)
        elif dtype is not None:
            try:
                source = dtype(source)
            except Exception:
                source = None
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


def resolve_arg_type(arg_type: Optional[type]):
    if arg_type is None:
        return ArgType.SINGLE, arg_type

    if hasattr(arg_type, '__origin__'):
        # handle generic type
        origin = getattr(arg_type, '__origin__')
        if origin is None:
            origin = arg_type

        argc = None
        etype = None
        if issubclass(origin, List):
            argc = ArgType.LIST
            if hasattr(arg_type, '__args__'):
                args = getattr(arg_type, '__args__')
                if args and len(args) == 1:
                    vt = args[0]
                    if not inspect.isclass(vt):
                        vt = None
                    etype = vt
        elif issubclass(origin, Mapping):
            argc = ArgType.DICT
            if hasattr(arg_type, '__args__'):
                args = getattr(arg_type, '__args__')
                if args and len(args) == 2:
                    kt = args[0]
                    vt = args[1]
                    if not inspect.isclass(kt):
                        kt = None
                    if not inspect.isclass(vt):
                        vt = None
                    etype = (kt, vt)
        elif issubclass(origin, Set):
            argc = ArgType.SET
            if hasattr(arg_type, '__args__'):
                args = getattr(arg_type, '__args__')
                if args and len(args) == 1:
                    vt = args[0]
                    if not inspect.isclass(vt):
                        vt = None
                    etype = vt
        if argc is None:
            raise ValueError('Unsupported generic argument type: {}'.format(arg_type))
        return argc, etype
    else:
        assert inspect.isclass(arg_type), 'Non-generic argument type must be a class, but got: {}'.format(arg_type)
        if issubclass(arg_type, List):
            return ArgType.LIST, None
        if issubclass(arg_type, Mapping):
            return ArgType.DICT, None
        if issubclass(arg_type, Set):
            return ArgType.SET, None
        return ArgType.SINGLE, arg_type


class ArgType:
    SINGLE = object()
    DICT = object()
    LIST = object()
    SET = object()
