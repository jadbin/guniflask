import inspect

from guniflask.annotation import Annotation, AnnotationUtils
from guniflask.context.annotation import Component


class Blueprint(Component):
    def __init__(self, url_prefix: str = None, **options):
        super().__init__()
        self['url_prefix'] = url_prefix
        self['options'] = options


def blueprint(url_prefix: str = None, **options):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Blueprint(url_prefix=url_prefix, **options))
        return func

    if inspect.isclass(url_prefix) or inspect.isfunction(url_prefix):
        f = url_prefix
        url_prefix = None
        return wrap_func(f)
    return wrap_func


class Route(Annotation):
    def __init__(self, rule: str = None, **options):
        super().__init__(rule=rule, options=options)


def route(rule: str = None, **options):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Route(rule=rule, **options))
        return func

    if inspect.isfunction(rule) or inspect.isclass(rule):
        f = rule
        rule = None
        return wrap_func(f)
    return wrap_func


def get_route(rule: str = None, **options):
    options['methods'] = ['GET']
    return route(rule=rule, **options)


def post_route(rule: str = None, **options):
    options['methods'] = ['POST']
    return route(rule=rule, **options)


def put_route(rule: str = None, **options):
    options['methods'] = ['PUT']
    return route(rule=rule, **options)


def patch_route(rule: str = None, **options):
    options['methods'] = ['PATCH']
    return route(rule=rule, **options)


def delete_route(rule: str = None, **options):
    options['methods'] = ['DELETE']
    return route(rule=rule, **options)
