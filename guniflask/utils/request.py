# coding=utf-8

from typing import get_type_hints, List, Any, Mapping, MutableMapping
import datetime as dt
import inspect

from .datatime import string_to_datetime
from .inspect import ArgType, resolve_arg_type


def map_object(source, dtype: Any = None, target=None) -> Any:
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

                prop_value = map_object(value, dtype=prop_type, target=prop)
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
            assert inspect.isclass(dtype), f'Cannot convert a list to {dtype}'
            collection_type = dtype

        result = []
        for v in source:
            result.append(map_object(v, dtype=etype))
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
