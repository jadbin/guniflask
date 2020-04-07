# coding=utf-8

from typing import Any

__all__ = [
    'FieldInfo',
    'RequestParam', 'RequestParamInfo',
    'PathVariable', 'PathVariableInfo',
    'RequestBody', 'RequestBodyInfo',
    'ContextParam', 'ContextParamInfo'
]


class FieldInfo:
    __slots__ = (
        'name',
        'default',
        'dtype',
        'description',
        'required',
        'extra',
    )

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', None)
        self.default = kwargs.pop('default', None)
        self.dtype = kwargs.pop('dtype', None)
        self.description = kwargs.pop('description', None)
        self.required = kwargs.pop('required', None)
        self.extra = kwargs


def RequestParam(name: str = None,
                 default: Any = None,
                 dtype: type = None,
                 description: str = None,
                 required: bool = None,
                 **extract: Any) -> Any:
    return RequestParamInfo(name=name,
                            default=default,
                            dtype=dtype,
                            description=description,
                            required=required,
                            **extract)


class RequestParamInfo(FieldInfo):
    pass


def PathVariable(name: str = None,
                 default: Any = None,
                 dtype: type = None,
                 description: str = None,
                 required: bool = None,
                 **extract: Any) -> Any:
    return PathVariableInfo(name=name,
                            default=default,
                            dtype=dtype,
                            description=description,
                            required=required,
                            **extract)


class PathVariableInfo(FieldInfo):
    pass


def RequestBody(name: str = None,
                default: Any = None,
                dtype: type = None,
                description: str = None,
                required: bool = None,
                **extract: Any) -> Any:
    return RequestBodyInfo(name=name,
                           default=default,
                           dtype=dtype,
                           description=description,
                           required=required,
                           **extract)


class RequestBodyInfo(FieldInfo):
    pass


def ContextParam(name: str = None,
                 default: Any = None,
                 dtype: type = None,
                 description: str = None,
                 required: bool = None,
                 **extract: Any) -> Any:
    return RequestParamInfo(name=name,
                            default=default,
                            dtype=dtype,
                            description=description,
                            required=required,
                            **extract)


class ContextParamInfo(FieldInfo):
    pass
