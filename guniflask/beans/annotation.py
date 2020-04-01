# coding=utf-8

from guniflask.annotation.core import Annotation, AnnotationUtils

__all__ = ['Autowired', 'autowired']


class Autowired(Annotation):
    def __init__(self):
        super().__init__()


def autowired(func):
    AnnotationUtils.add_annotation(func, Autowired())
    return func
