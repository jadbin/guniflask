# coding=utf-8

from functools import update_wrapper

from werkzeug.exceptions import Unauthorized

from guniflask.security.user_details import current_user, AnonymousUser

__all__ = ['login_required', 'roles_required', 'authorities_required']


def login_required(func):
    def wrapper(*args, **kwargs):
        if isinstance(current_user._get_current_object(), AnonymousUser):
            raise Unauthorized
        return func(*args, **kwargs)

    return update_wrapper(wrapper, func)


def roles_required(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not current_user.has_any_role(*roles):
                raise Unauthorized
            return func(*args, **kwargs)

        return update_wrapper(wrapper, func)

    return decorator


def authorities_required(*authorities):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not current_user.has_any_authority(*authorities):
                raise Unauthorized
            return func(*args, **kwargs)

        return update_wrapper(wrapper, func)

    return decorator
