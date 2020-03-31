# coding=utf-8

from typing import List, get_type_hints, Mapping, Union
import inspect

from guniflask.beans.definition import BeanDefinition
from guniflask.beans.factory import BeanFactory
from guniflask.beans.errors import BeanTypeNotDeclaredError, BeanTypeNotAllowedError, NoUniqueBeanDefinitionError, \
    BeansError

__all__ = ['ConstructorResolver']


class ConstructorResolver:
    def __init__(self, bean_factory: BeanFactory):
        self._bean_factory = bean_factory

    def instantiate(self, func):
        arg_spec = inspect.getfullargspec(func)
        NO_VALUE = object()
        if len(arg_spec.args) > 0 and arg_spec.args[0] in ('self', 'cls'):
            args = list(arg_spec.args)[1:]
        else:
            args = list(arg_spec.args)
        if arg_spec.defaults is not None:
            args_value = [NO_VALUE] * (len(args) - len(arg_spec.defaults)) + list(arg_spec.defaults)
        else:
            args_value = [NO_VALUE] * len(args)
        if arg_spec.kwonlydefaults is not None:
            kwargs_value = dict(arg_spec)
        else:
            kwargs_value = dict()
        hints = dict(arg_spec.annotations)

        for i, a in enumerate(args):
            required_type = hints.get(a)
            v = self._resolve_arg(a, required_type)
            if v is not None:
                args_value[i] = v
        for a in list(kwargs_value.keys()):
            required_type = hints.get(a)
            v = self._resolve_arg(a, required_type)
            if v is not None:
                kwargs_value[a] = v

        no_value_args = []
        for i, v in enumerate(args_value):
            if v == NO_VALUE:
                no_value_args.append(args[i])
        if len(no_value_args) > 0:
            raise ValueError('The following arguments cannot be resolved: {}'.format(', '.join(no_value_args)))
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
