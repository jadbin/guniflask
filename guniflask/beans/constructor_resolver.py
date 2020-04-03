# coding=utf-8

from typing import List, get_type_hints, Mapping, Union
import inspect

from guniflask.beans.definition import BeanDefinition
from guniflask.beans.factory import BeanFactory
from guniflask.beans.errors import BeanTypeNotDeclaredError, BeanTypeNotAllowedError, NoUniqueBeanDefinitionError, \
    BeansError
from guniflask.utils.factory import inspect_args

__all__ = ['ConstructorResolver']


class ConstructorResolver:
    def __init__(self, bean_factory: BeanFactory):
        self._bean_factory = bean_factory

    def instantiate(self, func):
        args, hints = inspect_args(func)

        args_value = []
        kwargs_value = {}
        for name, default in args.items():
            required_type = hints.get(name)
            v = self._resolve_arg(name, required_type)
            if default is inspect._empty:
                if v is None:
                    raise ValueError('The argument named "{}" cannot be resolved'.format(name))
                args_value.append(v)
            else:
                if v is None:
                    kwargs_value[name] = default
                else:
                    kwargs_value[name] = v

        return func(*args_value, **kwargs_value)

    def _resolve_arg(self, arg, required_type):
        bean = None
        arg_type, required_type = self._resolve_arg_type(required_type)

        if required_type is None:
            try:
                bean = self._bean_factory.get_bean(arg)
            except BeansError:
                pass
        else:
            candidates = self._bean_factory.get_beans_of_type(required_type)
            if arg_type == ArgType.DICT:
                bean = candidates
            elif arg_type == ArgType.LIST:
                bean = list(candidates.values())
            else:
                if len(candidates) == 1:
                    bean = list(candidates.values())[0]
                elif len(candidates) > 1:
                    if arg in candidates:
                        bean = candidates[arg]
                    else:
                        raise NoUniqueBeanDefinitionError(required_type)
        return bean

    def _resolve_bean_type(self, bean_name: str, bean_definition: BeanDefinition) -> type:
        source = bean_definition.source
        if inspect.isclass(source):
            return source
        if inspect.isfunction(source) or inspect.ismethod(source):
            hints = get_type_hints(source)
            if 'return' not in hints:
                raise BeanTypeNotDeclaredError(bean_name)
            bean_type = hints['return']
            if not inspect.isclass(bean_type):
                raise BeanTypeNotAllowedError(bean_name, bean_type)
            return bean_type

    def _resolve_arg_type(self, arg_type: Union[type, None]):
        if arg_type is not None and inspect.isclass(arg_type):
            if issubclass(arg_type, Mapping):
                if hasattr(arg_type, '__args__'):
                    args = getattr(arg_type, '__args__')
                    if args and len(args) == 2:
                        arg_type = args[1]
                return ArgType.DICT, arg_type
            if issubclass(arg_type, List):
                if hasattr(arg_type, '__args__'):
                    args = getattr(arg_type, '__args__')
                    if args and len(args) == 1:
                        arg_type = args[0]
                return ArgType.LIST, arg_type
        return ArgType.SINGLE, arg_type


class ArgType:
    SINGLE = object()
    DICT = object()
    LIST = object()
