import inspect

from guniflask.beans.errors import NoUniqueBeanDefinitionError, BeansError
from guniflask.beans.factory import BeanFactory
from guniflask.data_model.typing import inspect_args, analyze_arg_type


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
                    raise ValueError(f'The argument named "{name}" cannot be resolved')
                args_value.append(v)
            else:
                if v is None:
                    kwargs_value[name] = default
                else:
                    kwargs_value[name] = v

        return func(*args_value, **kwargs_value)

    def _resolve_arg(self, arg, required_type):
        bean = None
        arg_ = analyze_arg_type(required_type)

        if arg_.outer_type is None:
            try:
                bean = self._bean_factory.get_bean(arg)
            except BeansError:
                pass
        elif inspect.isclass(arg_.outer_type):
            candidates = self._bean_factory.get_beans_of_type(arg_.outer_type)
            if arg_.is_list():
                bean = list(candidates.values())
            elif arg_.is_set():
                bean = set(candidates.values())
            elif arg_.is_singleton():
                if len(candidates) == 1:
                    bean = list(candidates.values())[0]
                elif len(candidates) > 1:
                    if arg in candidates:
                        bean = candidates[arg]
                    else:
                        raise NoUniqueBeanDefinitionError(required_type)
        return bean
