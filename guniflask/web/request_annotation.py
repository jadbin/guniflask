from typing import Any


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
                 **extra: Any) -> Any:
    return RequestParamInfo(name=name,
                            default=default,
                            dtype=dtype,
                            description=description,
                            required=required,
                            **extra)


class RequestParamInfo(FieldInfo):
    pass


def PathVariable(name: str = None,
                 default: Any = None,
                 dtype: type = None,
                 description: str = None,
                 required: bool = None,
                 **extra: Any) -> Any:
    return PathVariableInfo(name=name,
                            default=default,
                            dtype=dtype,
                            description=description,
                            required=required,
                            **extra)


class PathVariableInfo(FieldInfo):
    pass


def RequestBody(name: str = None,
                default: Any = None,
                dtype: type = None,
                description: str = None,
                required: bool = None,
                **extra: Any) -> Any:
    return RequestBodyInfo(name=name,
                           default=default,
                           dtype=dtype,
                           description=description,
                           required=required,
                           **extra)


class RequestBodyInfo(FieldInfo):
    pass


def RequestHeader(name: str = None,
                  default: Any = None,
                  dtype: type = None,
                  description: str = None,
                  required: bool = None,
                  **extra: Any) -> Any:
    return RequestHeaderInfo(name=name,
                             default=default,
                             dtype=dtype,
                             description=description,
                             required=required,
                             **extra)


class RequestHeaderInfo(FieldInfo):
    pass


def CookieValue(name: str = None,
                default: Any = None,
                dtype: type = None,
                description: str = None,
                required: bool = None,
                **extra: Any) -> Any:
    return CookieValueInfo(name=name,
                           default=default,
                           dtype=dtype,
                           description=description,
                           required=required,
                           **extra)


class CookieValueInfo(FieldInfo):
    pass


def FormValue(name: str = None,
              default: Any = None,
              dtype: type = None,
              description: str = None,
              required: bool = None,
              **extra: Any) -> Any:
    return FormValueInfo(name=name,
                         default=default,
                         dtype=dtype,
                         description=description,
                         required=required,
                         **extra)


class FormValueInfo(FieldInfo):
    pass


def FilePart(name: str = None,
             default: Any = None,
             dtype: type = None,
             description: str = None,
             required: bool = None,
             **extra: Any) -> Any:
    return FilePartInfo(name=name,
                        default=default,
                        dtype=dtype,
                        description=description,
                        required=required,
                        **extra)


class FilePartInfo(FieldInfo):
    pass
