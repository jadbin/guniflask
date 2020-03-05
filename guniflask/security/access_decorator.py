# coding=utf-8

from functools import wraps

from werkzeug.exceptions import Unauthorized

from guniflask.security.user_details import current_user

__all__ = ['login_required', 'roles_required', 'authorities_required']


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user is None:
            raise Unauthorized
        return func(*args, **kwargs)

    return wrapper


def roles_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user is None or not current_user.has_any_role(*roles):
                raise Unauthorized
            return func(*args, **kwargs)

        return wrapper

    return decorator


def authorities_required(*authorities):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user is None or not current_user.has_any_authority(*authorities):
                raise Unauthorized
            return func(*args, **kwargs)

        return wrapper

    return decorator
