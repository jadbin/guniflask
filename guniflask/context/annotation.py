import inspect
from typing import Type, Collection, Union, Any

from guniflask.annotation import Annotation, AnnotationUtils, AnnotationMetadata
from guniflask.config.app_settings import settings
from guniflask.context.condition import Condition, ConditionContext


class Bean(Annotation):
    def __init__(self, name=None):
        super().__init__(name=name)


def bean(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Bean(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        f = name
        name = None
        return wrap_func(f)
    return wrap_func


class Autowired(Annotation):
    def __init__(self):
        super().__init__()


def autowired(func):
    AnnotationUtils.add_annotation(func, Autowired())
    return func


class Component(Annotation):
    def __init__(self, name=None):
        super().__init__(name=name)


def component(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Component(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        f = name
        name = None
        return wrap_func(f)
    return wrap_func


class Configuration(Component):
    def __init__(self, name=None):
        super().__init__(name=name)


def configuration(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Configuration(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        f = name
        name = None
        return wrap_func(f)
    return wrap_func


class Conditional(Annotation):
    def __init__(self, condition: Type[Condition]):
        super().__init__(condition=condition)


def conditional(condition: Union[Type[Condition], Condition]):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Conditional(condition))
        return func

    return wrap_func


class SettingCondition(Condition):
    def __init__(self, name: str, value: Any = None):
        self.name = name
        self.value = value

    def matches(self, context: ConditionContext, metadata: AnnotationMetadata) -> bool:
        v = settings.get_by_prefix(self.name)
        if self.value is None:
            return v is not None
        return v == self.value


def condition_on_setting(name: str, value: Any = None):
    return conditional(SettingCondition(name, value=value))


class Repository(Component):
    def __init__(self, name=None):
        super().__init__(name=name)


def repository(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Repository(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        f = name
        name = None
        return wrap_func(f)
    return wrap_func


class Service(Component):
    def __init__(self, name=None):
        super().__init__(name=name)


def service(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Service(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        f = name
        name = None
        return wrap_func(f)
    return wrap_func


class Controller(Component):
    def __init__(self, name=None):
        super().__init__(name=name)


def controller(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Controller(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        f = name
        name = None
        return wrap_func(f)
    return wrap_func


class Include(Annotation):
    def __init__(self, values: Collection = None):
        super().__init__(values=values)


def include(*values):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Include(values))
        return func

    return wrap_func
