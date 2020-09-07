# coding=utf-8

from typing import List, Set, Mapping, Optional
import inspect
from collections import OrderedDict


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
            raise ValueError(f'Unsupported generic argument type: {arg_type}')
        return argc, etype
    else:
        assert inspect.isclass(arg_type), f'Non-generic argument type must be a class, but got: {arg_type}'
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
