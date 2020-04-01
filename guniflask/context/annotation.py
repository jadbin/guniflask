# coding=utf-8

import inspect
from typing import Type, Collection

from guniflask.annotation.core import Annotation, AnnotationUtils
from guniflask.context.condition import Condition

__all__ = ['Bean', 'bean',
           'Component', 'component',
           'Configuration', 'configuration',
           'Conditional', 'conditional',
           'Repository', 'repository',
           'Service', 'service',
           'Controller', 'controller',
           'Include', 'include']


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


def conditional(condition: Type[Condition]):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Conditional(condition))
        return func

    return wrap_func


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
