# coding=utf-8

from typing import List

from guniflask.annotation.core import Annotation, AnnotationUtils

__all__ = ['FilterChain', 'filter_chain',
           'MethodFilter',
           'before_request', 'after_request',
           'app_before_request', 'app_after_request',
           'error_handler', 'app_error_handler']


class FilterChain(Annotation):
    def __init__(self, values: List = None):
        super().__init__(values=values)


def filter_chain(*values):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, FilterChain(list(values)))
        return func

    return wrap_func


class MethodFilter(Annotation):
    def add_method_filter(self, name, args=None):
        if 'values' not in self:
            self['values'] = []
        self['values'].append({'name': name, 'args': args})

    def get_method_filters(self):
        if 'values' not in self:
            return []
        return self['values']


def _add_method_filter_annotation(func, name, args=None):
    a = AnnotationUtils.get_annotation(func, MethodFilter)
    if a is None:
        a = MethodFilter()
        AnnotationUtils.add_annotation(func, a)
    a.add_method_filter(name, args=args)


def before_request(func):
    _add_method_filter_annotation(func, 'before_request')
    return func


def after_request(func):
    _add_method_filter_annotation(func, 'after_request')
    return func


def app_before_request(func):
    _add_method_filter_annotation(func, 'app_before_request')
    return func


def app_after_request(func):
    _add_method_filter_annotation(func, 'app_after_request')
    return func


def error_handler(code_or_exception):
    def wrap_func(func):
        _add_method_filter_annotation(func, 'errorhandler', args=[code_or_exception])
        return func

    return wrap_func


def app_error_handler(code_or_exception):
    def wrap_func(func):
        _add_method_filter_annotation(func, 'app_errorhandler', args=[code_or_exception])
        return func

    return wrap_func
