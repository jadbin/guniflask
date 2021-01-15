from functools import update_wrapper

from werkzeug.exceptions import Unauthorized

from guniflask.security.context import SecurityContext


def login_required(func):
    def wrapper(*args, **kwargs):
        user = SecurityContext.get_user()
        if user is None:
            raise Unauthorized
        return func(*args, **kwargs)

    return update_wrapper(wrapper, func)


def has_any_role(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = SecurityContext.get_user()
            if user is None or not SecurityContext.has_any_role(user, roles):
                raise Unauthorized
            return func(*args, **kwargs)

        return update_wrapper(wrapper, func)

    return decorator


def has_role(role):
    return has_any_role(role)


def has_any_authority(*authorities):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = SecurityContext.get_user()
            if user is None or not SecurityContext.has_any_authority(user, authorities):
                raise Unauthorized
            return func(*args, **kwargs)

        return update_wrapper(wrapper, func)

    return decorator


def has_authority(authority):
    return has_any_authority(authority)
