import datetime as dt
import inspect
from collections import OrderedDict
from typing import List, Set, Mapping, Optional
from typing import get_type_hints, Any, MutableMapping

from guniflask.utils.datatime import convert_to_datetime


def map_json(source: Any, dtype: Any = None, target: Any = None) -> Any:
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

                prop_value = map_json(value, dtype=prop_type, target=prop)
                if prop_value is not None:
                    setattr(target, key, prop_value)

            for key in type_hints:
                if not hasattr(target, key):
                    setattr(target, key, None)
        return target
    elif isinstance(source, List):
        if dtype is None:
            return source

        arg_ = analyze_arg_type(dtype)

        if arg_.is_list():
            collection_type = list
        elif arg_.is_set():
            collection_type = set
        else:
            assert inspect.isclass(dtype), f'Cannot convert a list to {dtype}'
            collection_type = dtype

        result = []
        for v in source:
            result.append(map_json(v, dtype=arg_.arg_type))
        if collection_type is not None:
            result = collection_type(result)
        return result
    else:
        if dtype == dt.datetime:
            source = convert_to_datetime(source)
        elif dtype is not None:
            try:
                source = dtype(source)
            except Exception:
                source = None
        return source


def inspect_args(func):
    signature = inspect.signature(func)
    parameters = signature.parameters
    return_type = signature.return_annotation

    hints = {}
    if return_type is not inspect._empty:
        hints['return'] = return_type

    args = OrderedDict()
    for p in parameters.values():
        args[p.name] = p.default
        if p.annotation is not inspect._empty:
            hints[p.name] = p.annotation

    return args, hints


class ArgTypeClass:
    CLASS = object()
    DICT = object()
    LIST = object()
    SET = object()


class ArgTypeResult:
    def __init__(self, arg_type_class, arg_type):
        self.arg_type = arg_type
        self._arg_type_class = arg_type_class

    def is_class(self):
        return self._arg_type_class is ArgTypeClass.CLASS

    def is_dict(self):
        return self._arg_type_class is ArgTypeClass.DICT

    def is_list(self):
        return self._arg_type_class is ArgTypeClass.LIST

    def is_set(self):
        return self._arg_type_class is ArgTypeClass.SET


def analyze_arg_type(arg_type: Optional[type]) -> ArgTypeResult:
    if arg_type is None:
        return ArgTypeResult(ArgTypeClass.CLASS, arg_type)

    if hasattr(arg_type, '__origin__'):
        # handle generic type
        origin = getattr(arg_type, '__origin__')
        if origin is None:
            origin = arg_type

        typec = None
        dtype = None
        if inspect.isclass(origin):
            if issubclass(origin, List):
                typec = ArgTypeClass.LIST
                if hasattr(arg_type, '__args__'):
                    args = getattr(arg_type, '__args__')
                    if args and len(args) == 1:
                        vt = args[0]
                        if not inspect.isclass(vt):
                            vt = None
                        dtype = vt
            elif issubclass(origin, Mapping):
                typec = ArgTypeClass.DICT
                if hasattr(arg_type, '__args__'):
                    args = getattr(arg_type, '__args__')
                    if args and len(args) == 2:
                        kt = args[0]
                        vt = args[1]
                        if not inspect.isclass(kt):
                            kt = None
                        if not inspect.isclass(vt):
                            vt = None
                        dtype = (kt, vt)
            elif issubclass(origin, Set):
                typec = ArgTypeClass.SET
                if hasattr(arg_type, '__args__'):
                    args = getattr(arg_type, '__args__')
                    if args and len(args) == 1:
                        vt = args[0]
                        if not inspect.isclass(vt):
                            vt = None
                        dtype = vt
        if typec is None:
            raise ValueError(f'Unsupported generic argument type: {arg_type}')
        return ArgTypeResult(typec, dtype)

    if not inspect.isclass(arg_type):
        raise ValueError(f'Non-generic argument type must be a class, but got: {arg_type}')
    if issubclass(arg_type, List):
        return ArgTypeResult(ArgTypeClass.LIST, None)
    if issubclass(arg_type, Mapping):
        return ArgTypeResult(ArgTypeClass.DICT, None)
    if issubclass(arg_type, Set):
        return ArgTypeResult(ArgTypeClass.SET, None)
    return ArgTypeResult(ArgTypeClass.CLASS, arg_type)
