# coding=utf-8

from typing import Collection
from guniflask.annotation.core import Annotation, AnnotationUtils

__all__ = ['FilterChain', 'filter_chain']


class FilterChain(Annotation):
    def __init__(self, values: Collection = None):
        super().__init__(values=values)


def filter_chain(*values):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, FilterChain(values))
        return func

    return wrap_func
