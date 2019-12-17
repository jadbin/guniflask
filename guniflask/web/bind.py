# coding=utf-8

__all__ = ['blueprint', 'route', 'get_route', 'post_route', 'put_route', 'patch_route', 'delete_route']


def blueprint(**options):
    def decorator(func):
        func.__is_blueprint = True
        func.__options = options
        return func

    return decorator


def route(rule, **options):
    def decorator(func):
        func.__is_route = True
        func.__rule = rule
        func.__options = options
        return func

    return decorator


def get_route(rule, **options):
    options['methods'] = ['GET']
    return route(rule, **options)


def post_route(rule, **options):
    options['methods'] = ['POST']
    return route(rule, **options)


def put_route(rule, **options):
    options['methods'] = ['PUT']
    return route(rule, **options)


def patch_route(rule, **options):
    options['methods'] = ['PATCH']
    return route(rule, **options)


def delete_route(rule, **options):
    options['methods'] = ['DELETE']
    return route(rule, **options)
