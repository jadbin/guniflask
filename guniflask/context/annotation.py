# coding=utf-8

import inspect

from guniflask.annotation.core import Annotation
from guniflask.annotation.annotation_utils import AnnotationUtils

__all__ = ['Bean', 'bean', 'Component', 'component', 'Configuration', 'configuration']


class Bean(Annotation):
    def __init__(self, name=None):
        super().__init__(name=name)


def bean(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Bean(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        return wrap_func(name)
    return wrap_func


class Component(Annotation):
    def __init__(self, name=None):
        super().__init__(name=name)


def component(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Component(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        return wrap_func(name)
    return wrap_func


class Configuration(Component):
    def __init__(self, name=None):
        super().__init__(name=name)


def configuration(name: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Configuration(name=name))
        return func

    if inspect.isclass(name) or inspect.isfunction(name):
        return wrap_func(name)
    return wrap_func
