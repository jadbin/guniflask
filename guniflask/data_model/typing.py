import builtins
import datetime as dt
import inspect
from collections import OrderedDict
from typing import Any, get_type_hints
from typing import List, Set, Mapping, Optional, Union

from pydantic import BaseModel
from pydantic.typing import get_origin, get_args

from guniflask.utils.datatime import convert_to_datetime


def parse_json(source: Any, dtype: Any = None) -> Any:
    if dtype is None:
        return source
    if source is None:
        return

    target = None
    arg_ = ArgType(dtype)

    if (arg_.is_list() or arg_.is_set()) and not isinstance(source, List):
        source = [source]

    if isinstance(source, Mapping):
        if arg_.is_singleton():
            if issubclass(arg_.outer_type, BaseModel):
                return arg_.outer_type(**source)

            target = arg_.outer_type()
            type_hints = get_type_hints(arg_.outer_type)
            for k, v in source.items():
                v_t = type_hints.get(k)
                vv = parse_json(v, dtype=v_t)
                setattr(target, k, vv)
        elif arg_.is_dict():
            target = dict()
            if arg_.outer_type is not None:
                k_t, v_t = arg_.outer_type
            else:
                k_t = v_t = None
            for k, v in source.items():
                kk = parse_json(k, dtype=k_t)
                vv = parse_json(v, dtype=v_t)
                target[kk] = vv

        if target is None:
            raise AssertionError(f'Cannot convert a dict to {dtype}')

    elif isinstance(source, List):
        collection_type = None
        if arg_.is_list():
            collection_type = list
        elif arg_.is_set():
            collection_type = set

        if collection_type is None:
            raise AssertionError(f'Cannot convert a list to {dtype}')

        target = []
        for v in source:
            target.append(parse_json(v, dtype=arg_.outer_type))
        target = collection_type(target)

    else:
        if arg_.is_singleton():
            if arg_.outer_type == dt.datetime:
                target = convert_to_datetime(source)
            else:
                if type(source) == arg_.outer_type:
                    target = source
                else:
                    target = arg_.outer_type(source)

    return target


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


class ArgTypeShape:
    SINGLETON = object()
    DICT = object()
    LIST = object()
    SET = object()
    UNION = object()


class ArgType:
    def __init__(self, arg_type):
        self.arg_type = arg_type

        self.shape = ArgTypeShape.SINGLETON
        self.outer_type = arg_type

        self._analyze_arg_type(arg_type)

    def is_singleton(self):
        return self.shape is ArgTypeShape.SINGLETON

    def is_dict(self):
        return self.shape is ArgTypeShape.DICT

    def is_list(self):
        return self.shape is ArgTypeShape.LIST

    def is_set(self):
        return self.shape is ArgTypeShape.SET

    def is_union(self):
        return self.shape is ArgTypeShape.UNION

    def _analyze_arg_type(self, arg_type: Optional[type]):
        if arg_type is None:
            return

        origin = get_origin(arg_type)
        if origin:
            shape = None
            dtype = None

            if origin is Union:
                allow_types = []

                for arg in get_args(arg_type):
                    if arg is not None:
                        allow_types.append(arg)

                self.shape = ArgTypeShape.UNION
                self.outer_type = [self._get_arg_type(t) for t in allow_types]
                return

            if inspect.isclass(origin):
                if issubclass(origin, List):
                    shape = ArgTypeShape.LIST
                    args = get_args(arg_type)
                    if args and len(args) == 1:
                        vt = args[0]
                        if not inspect.isclass(vt):
                            vt = None
                        dtype = self._get_arg_type(vt)
                elif issubclass(origin, Mapping):
                    shape = ArgTypeShape.DICT
                    args = get_args(arg_type)
                    if args and len(args) == 2:
                        kt = args[0]
                        vt = args[1]
                        dtype = (self._get_arg_type(kt), self._get_arg_type(vt))
                    else:
                        dtype = (None, None)
                elif issubclass(origin, Set):
                    shape = ArgTypeShape.SET
                    args = get_args(arg_type)
                    if args and len(args) == 1:
                        vt = args[0]
                        if not inspect.isclass(vt):
                            vt = None
                        dtype = self._get_arg_type(vt)
            if shape is None:
                raise ValueError(f'Unsupported generic argument type: {arg_type}')
            self.shape = shape
            self.outer_type = dtype
            return

        if isinstance(arg_type, str):
            if hasattr(builtins, arg_type):
                arg_type = getattr(builtins, arg_type)
                self.outer_type = arg_type

        if not inspect.isclass(arg_type):
            raise ValueError(f'Non-generic argument type must be a class, but got: {arg_type}')
        if issubclass(arg_type, List):
            self.shape = ArgTypeShape.LIST
            self.outer_type = None
        elif issubclass(arg_type, Mapping):
            self.shape = ArgTypeShape.DICT
            self.outer_type = (None, None)
        elif issubclass(arg_type, Set):
            self.shape = ArgTypeShape.SET
            self.outer_type = None

    def _get_arg_type(self, arg_type):
        try:
            result = self.__class__(arg_type)
        except Exception:
            result = self.__class__(None)
        if result.is_singleton():
            return result.outer_type
        return result


def analyze_arg_type(arg_type: Optional[type]) -> ArgType:
    return ArgType(arg_type)
