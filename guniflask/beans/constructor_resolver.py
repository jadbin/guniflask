# coding=utf-8

import inspect

from guniflask.beans.factory import BeanFactory
from guniflask.beans.errors import NoUniqueBeanDefinitionError, BeansError
from guniflask.utils.instantiation import inspect_args, resolve_arg_type, ArgType

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
        argc, etype = resolve_arg_type(required_type)

        if etype is None:
            try:
                bean = self._bean_factory.get_bean(arg)
            except BeansError:
                pass
        else:
            candidates = self._bean_factory.get_beans_of_type(etype)
            if argc is ArgType.DICT:
                bean = candidates
            elif argc is ArgType.LIST:
                bean = list(candidates.values())
            elif argc is ArgType.SET:
                bean = set(candidates.values())
            elif argc is ArgType.SINGLE:
                if len(candidates) == 1:
                    bean = list(candidates.values())[0]
                elif len(candidates) > 1:
                    if arg in candidates:
                        bean = candidates[arg]
                    else:
                        raise NoUniqueBeanDefinitionError(required_type)
        return bean
